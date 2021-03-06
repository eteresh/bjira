from bjira.operations import BJiraOperation
from bjira.utils import parse_portfolio_task


def _get_issue_type(args):
    return {
        'bg': 'Production Bug',
        'bug': 'Production Bug',

        'at': 'Autotesting Task',

        'hh': 'Задача'
    }.get(args.task_type, 'Задача')


def _get_prefix(args):
    if not args.service and args.task_type == 'at':
        return '[at] '
    elif args.service:
        return f'[{args.service}] '
    return ''


def _get_task_message(args):
    return _get_prefix(args) + args.message


class CreateJiraTask(BJiraOperation):

    def configure_arg_parser(self, subparsers):
        parser = subparsers.add_parser('create', help='create jira task')
        parser.add_argument(dest='task_type', default='hh', help='task type', nargs='?',
                            choices=('hh', 'at', 'test', 'bg', 'bag'))
        parser.add_argument('-s', dest='service', default=None,
                            help='task service - used for [{task service} prefix only')
        parser.add_argument('-p', dest='portfolio', default=None, help='[optional] portfolio to link')
        parser.add_argument('-m', dest='message', required=True, help='task name')
        parser.set_defaults(func=self._create_new_task)

    def _create_new_task(self, args):
        task_message = _get_task_message(args)
        print(f'creating task "{task_message}"')

        jira_api = self.get_jira_api()
        task = jira_api.create_issue(
            prefetch=True,
            fields={
                'project': 'HH',
                'issuetype': {'name': _get_issue_type(args)},
                'assignee': {'name': self.get_user()},
                'summary': task_message,
                'customfield_10961': {'value': self.get_team()}  # Development team
            }
        )
        print(self.get_task_url(task.key))

        if args.portfolio:
            portfolio_key = parse_portfolio_task(args.portfolio)
            jira_api.create_issue_link(
                type='Inclusion',
                inwardIssue=portfolio_key,
                outwardIssue=task.key
            )
            print(f'linked {self.get_task_url(task.key)} to {self.get_task_url(portfolio_key)}')
