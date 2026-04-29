from django.test import TestCase

from melodramatick.tasks import update_user_award_shared_task
from melodramatick.top_list.models import Award, Progress


class TasksTestCase(TestCase):
    fixtures = ['user.json', 'testtick_performance.json', 'testtick_company.json', 'testtick_venue.json',
                'testtick_top_list.json', 'testtick_work.json', 'testtick_testitem.json', 'testtick_composer.json']

    def test_update_user_award_shared_task(self):
        report = update_user_award_shared_task(user_id=1)
        self.assertEqual(report['lists_checked'], 2)
        self.assertEqual(report['awards_issued'], 2)
        self.assertEqual(set(str(a.level) for a in Award.objects.filter(user=1)), {'platinum'})
        self.assertEqual(set(p.ratio for p in Progress.objects.filter(user=1)), {1.0})

        report = update_user_award_shared_task(user_id=2)
        self.assertEqual(report['lists_checked'], 2)
        self.assertEqual(report['awards_issued'], 2)
        self.assertEqual(set(str(a.level) for a in Award.objects.filter(user=2)), {'platinum', 'bronze'})
        self.assertEqual(set(p.ratio for p in Progress.objects.filter(user=2)), {1.0, 0.5})

        report = update_user_award_shared_task(user_id=1, performance_id=2)
        self.assertEqual(report['lists_checked'], 1)
        self.assertEqual(report['awards_issued'], 0)  # Already awarded
