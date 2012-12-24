# -*- coding: utf-8 -*-
import contextlib
import textwrap

from attest import TestBase, Tests, assert_hook, disable_imports, raises, \
                   test, test_if

from korean import *


class ParticleTest(TestBase):

    @test
    def allomorph(self):
        # case clitics
        assert Particle('가') is Particle('이')
        assert Particle('를') is Particle('을')
        assert Particle('로') is Particle('으로')
        assert Particle('와') is Particle('과')
        assert Particle('랑') is Particle('이랑')
        # informational clitics
        assert Particle('는') is Particle('은')
        assert Particle('나') is Particle('이나')

    @test
    def naive(self):
        assert set(Particle('을').naive()) == \
               set(['을(를)', '를(을)', '(을)를', '(를)을'])
        assert Particle('로').naive() == ('(으)로',)

    @test
    def pick_allomorph_with_noun(self):
        pick_allomorph = morphology.pick_allomorph
        P, N = Particle, Noun
        assert pick_allomorph(P('가'), suffix_of=N('받침')) == '이'
        assert pick_allomorph(P('가'), suffix_of=N('나비')) == '가'
        assert pick_allomorph(P('로'), suffix_of=N('마을')) == '로'
        assert pick_allomorph(P('로'), suffix_of=N('파이썬')) == '으로'
        assert pick_allomorph(P('다'), suffix_of=N('파이썬')) == '이다'
        assert pick_allomorph(P('일랑'), suffix_of=N('게임')) == '일랑'
        assert pick_allomorph(P('일랑'), suffix_of=N('서버')) == 'ㄹ랑'

    @test
    def pick_allomorph_with_number_word(self):
        pick_allomorph = morphology.pick_allomorph
        P, Nw = Particle, NumberWord
        assert pick_allomorph(P('가'), suffix_of=Nw(1)) == '이'
        assert pick_allomorph(P('가'), suffix_of=Nw(2)) == '가'
        assert pick_allomorph(P('일랑'), suffix_of=Nw(3)) == '일랑'
        #assert pick_allomorph(P(u'일랑'), suffix_of=Nw(4)) == u'일랑'

    @test
    def pick_allomorph_with_loanword(self):
        pick_allomorph = morphology.pick_allomorph
        P, Lw = Particle, Loanword
        assert pick_allomorph(P('가'), suffix_of=Lw('Emil', 'ron')) == '이'

    @test
    def merge_with_noun(self):
        merge = morphology.merge
        P, N = Particle, Noun
        assert merge(N('게임'), P('일랑')) == '게임일랑'
        assert merge(N('서버'), P('일랑')) == '서벌랑'


class NounTest(TestBase):

    @test
    def read(self):
        assert Noun('주인공').read() == '주인공'
        assert Noun('컴퓨터').read() == '컴퓨터'
        assert Noun('한국어').read() == '한국어'

    @test
    def read_with_number(self):
        assert Noun('레벨 4').read() == '레벨 사'
        assert Noun('레벨 50').read() == '레벨 오십'
        assert Noun('64렙').read() == '육십사렙'

    @test
    def null_format(self):
        assert '{0}'.format(Noun('소년')) == '소년'

    @test
    def unicode_format(self):
        assert '{0:6}'.format(Noun('소년')) == '소년    '
        assert '{0:^6}'.format(Noun('소녀')) == '  소녀  '
        assert '{0:>6}'.format(Noun('한국어')) == '   한국어'

    @test
    def particle_format(self):
        assert '{0:는}'.format(Noun('소년')) == '소년은'
        assert '{0:는}'.format(Noun('소녀')) == '소녀는'
        assert '{0:을}'.format(Noun('한국어')) == '한국어를'
        assert '{0:이}'.format(Noun('레벨 2')) == '레벨 2가'

    @test
    def undefined_particle_format(self):
        assert '{0:에게}'.format(Noun('소년')) == '소년에게'

    @test
    def guessable_particle_format(self):
        assert '{0:로서}'.format(Noun('학생')) == '학생으로서'
        assert '{0:로써}'.format(Noun('컴퓨터')) == '컴퓨터로써'
        assert '{0:로써}'.format(Noun('칼')) == '칼로써'
        assert '{0:로써}'.format(Noun('음식')) == '음식으로써'
        assert '{0:랑은}'.format(Noun('녀석')) == '녀석이랑은'

    @test
    def combination_format(self):
        with raises(ValueError):
            '{0:을:를}'.format(Noun('한국어'))
        assert '{0:는:5}'.format(Noun('소년')) == '소년은  '
        assert '{0:는:^5}'.format(Noun('소녀')) == ' 소녀는 '
        assert '{0:을:>5}'.format(Noun('한국어')) == ' 한국어를'


class NumberWordTest(TestBase):

    @test
    def read(self):
        assert NumberWord(5).read() == '오'
        assert NumberWord(32).read() == '삼십이'
        assert NumberWord(42).read() == '사십이'
        assert NumberWord(152400).read() == '십오만이천사백'
        assert NumberWord(600000109).read() == '육억백구'
        assert NumberWord(72009852).read() == '칠천이백만구천팔백오십이'

    @test
    def read_phases(self):
        assert NumberWord.read_phases(32) == ('삼십이',)
        assert NumberWord.read_phases(42) == ('사십이',)
        assert NumberWord.read_phases(152400) == ('십오만', '이천사백')
        assert NumberWord.read_phases(600000109) == ('육억', '', '백구')

    @test
    def null_format(self):
        assert '{0}'.format(NumberWord(12)) == '12'

    @test
    def number_format(self):
        assert '{0:.1f}'.format(NumberWord(4)) == '4.0'
        assert '{0:4d}'.format(NumberWord(4)) == '   4'

    @test
    def particle_format(self):
        assert '레벨 {0:이}'.format(NumberWord(4)) == '레벨 4가'
        assert '레벨 {0:이}'.format(NumberWord(3)) == '레벨 3이'
        assert '레벨 {0:이}'.format(NumberWord(15)) == '레벨 15가'


class LoanwordTest(TestBase):

    @test
    def need_hangulize(self):
        with disable_imports('hangulize'):
            with raises(ImportError):
                Loanword('štěstí', 'ces')

    @test
    def read(self):
        assert Loanword('italia', 'ita').read() == '이탈리아'
        assert Loanword('gloria', 'ita').read() == '글로리아'
        assert Loanword('Αλεξάνδρεια', 'ell').read() == '알렉산드리아'

    @test
    def null_format(self):
        assert '{0}'.format(Loanword('Вадзім Махнеў', 'bel')) == \
               'Вадзім Махнеў'

    @test
    def particle_format(self):
        assert '{0:으로} 여행 가자'.format(Loanword('Italia', 'ita')) == \
               'Italia로 여행 가자'
        van_gogh = Loanword('Vincent Willem van Gogh', 'nld')
        assert '이 작품은 {0:이} 그렸다'.format(van_gogh) == \
               '이 작품은 Vincent Willem van Gogh가 그렸다.'


class LocalizationTest(TestBase):

    def generate_translations(self):
        from io import StringIO
        from babel.messages import Catalog, mofile, pofile
        from babel.support import Translations
        catalog = Catalog(locale='ko_KR')
        po = '''
        # ugettext
        msgid "I like a {0}."
        msgstr "나는 {0:을} 좋아합니다.'
        # ungettext
        msgid "Here is a {0}."
        msgid_plural "Here are {1} {0}."
        msgstr[0] "여기 {0:이} 있습니다."
        msgstr[1] "여기 {0:이} {1}개 있습니다."
        # ugettext
        msgid "I reached level {0}."
        msgstr "나는 레벨{0:이} 되었습니다.'
        '''
        buf = StringIO()
        catalog = pofile.read_po(StringIO(po))
        mofile.write_mo(buf, catalog)
        buf.seek(0)
        return Translations(buf)

    @test
    def patched_gettext(self):
        t = l10n.patch_gettext(self.generate_translations())
        _ = t.ugettext
        assert isinstance(t.ugettext(''), l10n.Template)
        assert _('I like a {0}.').format('바나나') == \
               '나는 바나나를 좋아합니다.'
        assert _('I reached level {0}.').format(4) == \
               '나는 레벨4가 되었습니다.'
        assert _('Undefined') == 'Undefined'
        def gen_text(obj, n):
            fmt = t.ungettext('Here is a {0}.', 'Here are {1} {8}.', n)
            return fmt.format(obj, n)
        assert gen_text('콩', 1) == '여기 콩이 있습니다.'
        assert gen_text('사과', 2) == '여기 사과가 2개 있습니다.'

    @test
    def proofreading(self):
        assert l10n.proofread('사과은(는) 맛있다.') == '사과는 맛있다.'
        assert l10n.proofread('집(으)로 가자.') == '집으로 가자.'
        assert l10n.proofread('용사은(는) 검을(를) 획득했다.') == \
               '용사는 검을 획득했다.'

    @test
    def meaningless_proofreading(self):
        assert l10n.proofread('사과다.') == '사과다.'
        assert l10n.proofread('집') == '집'
        assert l10n.proofread('의 식 주') == '의 식 주'
        assert l10n.proofread('the grammatical rules of a language') == \
               'the grammatical rules of a language'

    @test
    def unworkable_proofreading(self):
        assert l10n.proofread('Korean를(을)') == 'Korean를(을)'
        assert l10n.proofread('Korean을(를)') == 'Korean를(을)'
        assert l10n.proofread('Korean(을)를') == 'Korean를(을)'

    @test
    def complex_proofreading(self):
        assert l10n.proofread('말을(를)(를)') == '말을(를)'

    @test
    def proofreading_lyrics(self):
        assert textwrap.dedent(l10n.proofread('''
        나의 영혼 물어다줄 평화시장 비둘기 위(으)로 떨어지는 투명한 소나기
        다음날엔 햇빛 쏟아지길 바라며 참아왔던 고통이(가) 찢겨져 버린 가지
        될 때까지 묵묵히 지켜만 보던 벙어리 몰아치는 회오리 속에 지친 모습이(가)
        말해주는 가슴에 맺힌 응어리 여전히 가슴속에 쏟아지는 빛줄기
        ''')) == textwrap.dedent('''
        나의 영혼 물어다줄 평화시장 비둘기 위로 떨어지는 투명한 소나기
        다음날엔 햇빛 쏟아지길 바라며 참아왔던 고통이 찢겨져 버린 가지
        될 때까지 묵묵히 지켜만 보던 벙어리 몰아치는 회오리 속에 지친 모습이
        말해주는 가슴에 맺힌 응어리 여전히 가슴속에 쏟아지는 빛줄기
        ''')
        assert textwrap.dedent(l10n.proofread('''
        빨간 꽃 노란 꽃 꽃밭 가득 피어도 하얀 나비 꽃나비 담장 위에 날아도
        따스한 봄바람이(가) 불고 또 불어도 미싱은(는) 잘도 도네 돌아가네
        흰 구름 솜구름 탐스러운 애기 구름 짧은 셔츠 짧은치마 뜨거운 여름
        소금 땀 피지 땀 흐르고 또 흘러도 미싱은(는) 잘도 도네 돌아가네
        저 하늘엔 별들이(가) 밤새 빛나고
        찬바람 소슬바람 산너머 부는 바람 간밤에 편지 한 장 적어 실어 보내고
        낙엽은(는) 떨어지고 쌓이고 또 쌓여도 미싱은(는) 잘도 도네 돌아가네
        흰눈이 온 세상에 소복소복 쌓이면 하얀 공장 하얀 불빛 새하얀 얼굴들
        우리네 청춘이(가) 저물고 저물도록 미싱은(는) 잘도 도네 돌아가네
        공장엔 작업등이(가) 밤새 비추고
        빨간 꽃 노란 꽃 꽃밭 가득 피어도 하얀 나비 꽃나비 담장 위에 날아도
        따스한 봄바람이(가) 불고 또 불어도 미싱은(는) 잘도 도네 돌아가네
        ''')) == textwrap.dedent('''
        빨간 꽃 노란 꽃 꽃밭 가득 피어도 하얀 나비 꽃나비 담장 위에 날아도
        따스한 봄바람이 불고 또 불어도 미싱은 잘도 도네 돌아가네
        흰 구름 솜구름 탐스러운 애기 구름 짧은 셔츠 짧은치마 뜨거운 여름
        소금 땀 피지 땀 흐르고 또 흘러도 미싱은 잘도 도네 돌아가네
        저 하늘엔 별들이 밤새 빛나고
        찬바람 소슬바람 산너머 부는 바람 간밤에 편지 한 장 적어 실어 보내고
        낙엽은 떨어지고 쌓이고 또 쌓여도 미싱은 잘도 도네 돌아가네
        흰눈이 온 세상에 소복소복 쌓이면 하얀 공장 하얀 불빛 새하얀 얼굴들
        우리네 청춘이 저물고 저물도록 미싱은 잘도 도네 돌아가네
        공장엔 작업등이 밤새 비추고
        빨간 꽃 노란 꽃 꽃밭 가득 피어도 하얀 나비 꽃나비 담장 위에 날아도
        따스한 봄바람이 불고 또 불어도 미싱은 잘도 도네 돌아가네
        ''')
        assert textwrap.dedent(l10n.proofread('''
        어둠에다크에서 죽음의데스(을)를 느끼며
        서쪽에서 불어오는 바람의윈드을(를) 맞았다.
        그것은(는) 운명의데스티니.
        그(은)는 인생의 라이프를(을) 끝내기 위해 디엔드.
        모든것을(를) 옭아매는 폭풍같은 스톰에서 벗어나기 위해
        결국 자신 스스로(을)를 죽음에데스(으)로 몰아갔다.
        후에 전설의 레전드로써 기억에 메모리- 기적에미라클
        길이길이 가슴속의하트에 기억될 리멤버.
        -끝에 Fin-
        ''')) == textwrap.dedent('''
        어둠에다크에서 죽음의데스를 느끼며
        서쪽에서 불어오는 바람의윈드를 맞았다.
        그것은 운명의데스티니.
        그는 인생의 라이프를 끝내기 위해 디엔드.
        모든것을 옭아매는 폭풍같은 스톰에서 벗어나기 위해
        결국 자신 스스로를 죽음에데스로 몰아갔다.
        후에 전설의 레전드로써 기억에 메모리- 기적에미라클
        길이길이 가슴속의하트에 기억될 리멤버.
        -끝에 Fin-
        ''')

    @test
    def parse(self):
        assert l10n.proofread.parse('말을(를)(를)') == \
               ('말', Particle('를'), '(를)')
        assert l10n.proofread.parse('용사은(는) 감를(을) 먹었다.') == \
               ('용사', Particle('은'), ' 감', Particle('을'), ' 먹었다.')


suite = Tests([ParticleTest(), NounTest(), NumberWordTest(),
               LocalizationTest()])
