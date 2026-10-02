import unittest
from collect import parse,collect

HTML='<article class="Box-row"><h2><a href="/org/repo">Repo</a></h2><p>A &amp; B</p><a href="/org/repo/stargazers">1,234</a><span>120 stars today</span></article>'

class CollectorTests(unittest.TestCase):
    def test_parse(self):
        row=parse(HTML,'daily')[0]
        self.assertEqual((row['repo'],row['rank'],row['stars'],row['period_stars']),('org/repo',1,1234,120))
        self.assertEqual(row['description'],'A & B')
        self.assertIsNone(parse(HTML,'weekly')[0]['period_stars'])

    def test_malformed_and_duplicate(self):
        for source in ('<html>Login</html>',HTML+HTML,HTML.replace('/org/repo','/../repo')):
            with self.assertRaises(ValueError):parse(source,'daily')

    def test_failure_retains_last_success(self):
        prior,failed=collect({},lambda period:HTML)
        self.assertEqual(failed,[])
        def fail(period):raise ValueError('Do not expose sensitive exception bodies')
        result,failed=collect(prior,fail)
        self.assertEqual(len(failed),3)
        self.assertEqual(result['periods']['daily']['fetched_at'],prior['periods']['daily']['fetched_at'])
        self.assertEqual(result['periods']['daily']['items'],prior['periods']['daily']['items'])
        self.assertEqual(result['periods']['daily']['status'],'failed')

if __name__=='__main__':unittest.main()
