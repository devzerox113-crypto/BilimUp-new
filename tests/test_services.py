import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.database import DB
from services.auth import Auth
from services.question_service import QuestionService
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class T(unittest.TestCase):
    def setUp(s): s.db = DB(':memory:'); s.a = Auth(s.db); s.q = QuestionService(BASE, s.db)
    def test_auth(s):
        pw = s.a.bootstrap_admin(); s.assertIsNone(s.a.bootstrap_admin())
        s.assertEqual(s.a.login('admin', pw)[1], 'ok'); s.assertEqual(s.a.login('admin', 'x')[1], 'bad')
        s.assertTrue(s.a.create('Ali', 'secret1')); s.assertFalse(s.a.create('ali', 'secret1')); s.assertFalse(s.a.create('b', '123'))
        s.a.set_blocked('ali', True); s.assertEqual(s.a.login('ali', 'secret1')[1], 'blocked')
        s.a.set_blocked('ali', False); new = s.a.reset('ali'); s.assertEqual(s.a.login('ali', new)[1], 'ok'); s.assertEqual(s.a.login('ali', 'secret1')[1], 'bad')
        s.assertNotIn(pw, s.db.q('select pw from users')[0]['pw'])
    def test_first_run(s):
        pw = s.a.first_run_password(); s.assertEqual(s.a.login('admin', pw)[1], 'ok')
        pw2 = s.a.first_run_password(); s.assertEqual(s.a.login('admin', pw2)[1], 'ok'); s.assertNotEqual(pw, pw2)
        s.a.mark_admin_seen(); s.assertIsNone(s.a.first_run_password())
    def test_contact_rank(s):
        from services import contact; u = contact.wa_url(contact.NUMBERS[0], 'Сәлем: ')
        s.assertTrue(u.startswith('https://wa.me/77074548249?text=%D0%A1')); s.assertEqual(contact.pretty('+77077153750'), '+7 707 715 3750')
        s.a.create('a', 'secret1'); s.a.create('b', 'secret1'); s.db.add_result('a', {'math': (3, 3)}); s.assertEqual((s.db.rank('a'), s.db.rank('b')), (1, 2)); s.assertTrue(s.db.daily('a', 0))
    def test_questions_stats(s):
        m = s.q.mix(['math'], 10); s.assertEqual(len(m), 3)
        for q in m: s.assertIn(q['a'], range(4))
        s.assertTrue(s.q.add('math', 'Q?', ['1', '2', '3', '4'], 2, 'e')); s.assertFalse(s.q.add('math', 'Q?', ['1', '1', '3', '4'], 2)); s.assertEqual(s.q.count('math'), 4)
        s.a.create('ali', 'secret1'); s.assertEqual(s.db.add_result('ali', {'math': (2, 3)}), 20)
        s.assertEqual(s.db.summary('ali'), (1, 2, 3)); s.assertEqual(s.db.streak('ali'), 1); s.assertEqual(s.db.leaderboard()[0]['points'], 20)
    def test_calc_update(s):
        from services.calculator import calc; from services import updater
        s.assertEqual(calc('2+3×4'), '14'); s.assertEqual(calc('2^10'), '1024'); s.assertEqual(calc('sqrt(144)'), '12'); s.assertEqual(calc('sin(30)'), '0.5')
        for bad in ('__import__("os")', '1/0', '9^9999', '(('): s.assertEqual(calc(bad), 'Error')
        d = {'version': '0.3.0', 'apk_url': 'http://x/a.apk', 'questions': [{'s': 'math', 'q': 'N1?', 'o': ['1', '2', '3', '4'], 'a': 0, 'e': ''}, {'s': 'math', 'q': 'N1?', 'o': ['1', '2', '3', '4'], 'a': 0}, {'bad': 1}]}
        r = updater.apply(d, '0.2.0', s.q); s.assertEqual((r['apk'], r['added']), ('http://x/a.apk', 1)); s.assertIsNone(updater.apply(d, '0.3.0', s.q)['apk'])
    def test_data(s):
        import json; e = json.load(open(os.path.join(BASE, 'assets', 'periodic_table.json'), encoding='utf-8')); s.assertEqual([x['n'] for x in e], list(range(1, 119)))
        s.db.add_mistake('a', {'q': 'x', 's': 'math', 'o': [], 'a': 0}); s.assertEqual(len(s.db.mistakes('a')), 1); s.db.del_mistake('a', {'q': 'x'}); s.assertEqual(s.db.mistakes('a'), [])
if __name__ == '__main__': unittest.main()
