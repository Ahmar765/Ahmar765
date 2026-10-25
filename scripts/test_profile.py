"""Offline regression checks for calendar counts and generated SVGs."""
from datetime import date, timedelta
import unittest
from xml.etree import ElementTree

from build_profile import CalendarParser, ROOT, statistics


class ProfileTests(unittest.TestCase):
    def test_accessible_tooltips_supply_counts(self):
        parser = CalendarParser()
        start = date(2025, 1, 1)
        for index in range(365):
            day = start + timedelta(days=index)
            count = index % 3
            label = f'{count} contributions' if count else 'No contributions'
            parser.feed(f'<td id="day-{index}" data-date="{day}" data-level="{count}"></td><tool-tip for="day-{index}">{label} on January 1.</tool-tip>')
        days = parser.days()
        self.assertEqual(len(days), 365)
        self.assertEqual(sum(item['count'] for item in days), 364)

    def test_incomplete_or_changed_calendar_fails(self):
        parser = CalendarParser()
        parser.feed('<td data-date="2025-01-01" data-level="2"></td>')
        with self.assertRaises(ValueError):
            parser.days()

    def test_streak_allows_unfinished_today(self):
        days = [{'date': f'2025-01-{index:02}', 'count': count} for index, count in enumerate([0, 4, 1, 0], 1)]
        self.assertEqual(statistics(days), (5, 2, 2))

    def test_all_artwork_is_well_formed(self):
        for name in ['avi-ascii.svg', 'info-card.svg', 'contrib-heatmap.svg']:
            root = ElementTree.parse(ROOT / name).getroot()
            self.assertEqual(root.tag, '{http://www.w3.org/2000/svg}svg')
            self.assertFalse(root.findall('.//{http://www.w3.org/2000/svg}script'))


if __name__ == '__main__':
    unittest.main()
