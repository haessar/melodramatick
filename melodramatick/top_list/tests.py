from django.test import TestCase

from .views import TopListView


class TopListViewTestCase(TestCase):
    fixtures = ["contenttypes.json", "composer.json", "sites.json", "top_list.json", "user.json", "work.json", "opera.json"]

    def setUp(self):
        response = self.client.get("/")
        self.request = response.wsgi_request
        self.view = TopListView()
        self.view.setup(self.request)

    def test_get_table_data(self):
        table_data = self.view.get_table_data()
        if self.request.site.id == 1:
            self.assertListEqual(
                list(table_data.values('max_position', 'list_work_count').order_by('id')),
                [{'max_position': 2, 'list_work_count': 2},  # <List: Top operas - Example Dot Com>
                 {'max_position': 1, 'list_work_count': 1}]  # <List: Another List - Example Dot Com>
            )
        elif self.request.site.id == 2:
            # TODO - Write top_list fixtures for balletick
            pass
