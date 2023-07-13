import datetime

import convertapi
from docxtpl import DocxTemplate
from types import SimpleNamespace
from typing import Dict


def check_nonetype(data) -> str:
    return data if data is not None else 'Нет данных'


def data_create(card: Dict, fns_card: Dict, affilation_company: Dict, court_arbitration: Dict, zakupki_top: Dict,
                fssp_list: Dict, proverki: Dict, licenses: Dict, important_facts: Dict) -> SimpleNamespace:
    data = SimpleNamespace()

    data.date = check_nonetype(datetime.datetime.now().strftime('%d.%m.%Y'))
    data.legal_entity_name = check_nonetype(card.get('НаимЮЛСокр', 'Нет данных'))
    data.full_name = check_nonetype(card.get('НаимЮЛПолн', 'Нет данных'))
    data.status = check_nonetype(card.get('Активность', 'Нет данных'))
    data.legal_address = check_nonetype(card.get('Адрес', 'Нет данных'))
    try:
        data.authorized_capital = int(card.get('СумКап'))
    except Exception:
        data.authorized_capital = check_nonetype(card.get('СумКап', 'Нет данных'))
    for executives in card.get('Руководители', []):
        if executives.get('fl'):
            data.director_general = executives.get('fl')
            spec_2 = card.get('mass_leaders')
            data.spec_fns_2 = 'состоит' if spec_2 else 'не состоит'
            break
    else:
        data.director_general = 'Нет данных'
        data.spec_fns_2 = 'не состоит'
    data.average_headcount = check_nonetype(card.get('ЧислСотруд', 'Нет данных'))
    data.principal_activity_code = check_nonetype(card.get('КодОКВЭД', 'Нет данных'))
    data.principal_activity = check_nonetype(card.get('НаимОКВЭД', 'Нет данных'))
    svokveddop = card.get('СвОКВЭДДоп', [])
    if svokveddop is not None:
        data.total_activities = len(svokveddop)
    else:
        data.total_activities = 0
    data.ogrn = check_nonetype(card.get('ОГРН', 'Нет данных'))
    data.inn = check_nonetype(card.get('ИНН', 'Нет данных'))
    data.kpp = check_nonetype(card.get('КПП', 'Нет данных'))
    data.register_date = check_nonetype(fns_card.get('СвРегОрг', {}).get('ГРНДата', {}).get('@attributes', {}).get('ДатаЗаписи', 'Нет данных'))
    data.registrar = check_nonetype(fns_card.get('СвРегОрг', {}).get('@attributes', {}).get('НаимНО', 'Нет данных'))
    data.registrar_address = check_nonetype(fns_card.get('СвРегОрг', {}).get('@attributes', {}).get('АдрРО', 'Нет данных'))
    data.date_registration = check_nonetype(fns_card.get('СвУчетНО', {}).get('@attributes', {}).get('ДатаПостУч', 'Нет данных'))
    data.tax_authority = check_nonetype(fns_card.get('СвУчетНО', {}).get('СвНО', {}).get('@attributes', {}).get('НаимНО', 'Нет данных'))
    data.revenue_2022 = check_nonetype(card.get('ФО2022', {}).get('ВЫРУЧКА', 'Нет данных'))
    data.profit_2022 = check_nonetype(card.get('ФО2022', {}).get('ПРИБЫЛЬ', 'Нет данных'))
    data.cost_2022 = check_nonetype(card.get('ФО2022', {}).get('ОСНСРЕДСТВА', 'Нет данных'))
    data.revenue_2021 = check_nonetype(card.get('ФО2021', {}).get('ВЫРУЧКА', 'Нет данных'))
    data.profit_2021 = check_nonetype(card.get('ФО2021', {}).get('ПРИБЫЛЬ', 'Нет данных'))
    data.cost_2021 = check_nonetype(card.get('ФО2021', {}).get('ОСНСРЕДСТВА', 'Нет данных'))
    data.revenue_2020 = check_nonetype(card.get('ФО2020', {}).get('ВЫРУЧКА', 'Нет данных'))
    data.profit_2020 = check_nonetype(card.get('ФО2020', {}).get('ПРИБЫЛЬ', 'Нет данных'))
    data.cost_2020 = check_nonetype(card.get('ФО2020', {}).get('ОСНСРЕДСТВА', 'Нет данных'))
    if affilation_company.get('total') == 0:
        data.affilation_company = 'Связанных организаций и индивидуальных предпринимателей не выявлено'
    else:
        data.affilation_company = f'У {data.legal_entity_name} найдено {affilation_company.get("total")} связанных организаций и индивидуальных предпринимателей'
    data.count_court_cases = court_arbitration.get('всего', 0)
    data.respondent = card.get('СудыСтатистика', {}).get('Ответчик', {}).get('Количество', 0)
    data.plaintiff = card.get('СудыСтатистика', {}).get('Истец', {}).get('Количество', 0)
    data.claims = card.get('СудыСтатистика', {}).get('Ответчик', {}).get('Сумма', 0) + card.get('СудыСтатистика', {}).get('Истец', {}).get('Сумма', 0)
    data.third_party = data.count_court_cases - data.respondent - data.plaintiff
    total_buying = zakupki_top.get('total', 0)
    data.total_buying = zakupki_top.get('total', 0)
    if total_buying == 0:
        data.money_buying = 0
    else:
        money_buying = sum(int(doc.get('sum', 0)) for doc in zakupki_top.get('docs', []) if doc.get('sum') is not None)
        data.money_buying = money_buying
    try:
        data.proceedings_total = fssp_list.get('total', 0)
    except AttributeError:
        data.proceedings_total = 0
    try:
        if fssp_list.get('total', 0) == 0:
            data.proceedings_fine = 0
            data.proceedings_no = 0
            data.proceedings_other = 0
            data.proceedings_money = 0
            data.proceedings_money_get = 0
        else:
            proceedings_fine = sum(1 for doc in fssp_list.get('docs', []) if doc.get('ПредметИсп') is not None and 'штраф' in doc.get('ПредметИсп').lower())
            proceedings_no = sum(1 for doc in fssp_list.get('docs', []) if doc.get('ПредметИсп') is None)
            proceedings_other = sum(1 for doc in fssp_list.get('docs', []) if doc.get('ПредметИсп') is not None and 'штраф' not in doc.get('ПредметИсп').lower())
            proceedings_money = sum(doc.get('СуммаДолга', 0) for doc in fssp_list.get('docs', []) if doc.get('СуммаДолга') is not None)
            proceedings_money_get = sum(doc.get('ОстатокДолга', 0) for doc in fssp_list.get('docs', []) if doc.get('ОстатокДолга') is not None)
            data.proceedings_fine = proceedings_fine
            data.proceedings_no = proceedings_no
            data.proceedings_other = proceedings_other
            data.proceedings_money = proceedings_money
            data.proceedings_money_get = proceedings_money_get
    except AttributeError:
        data.proceedings_fine = 0
        data.proceedings_no = 0
        data.proceedings_other = 0
        data.proceedings_money = 0
        data.proceedings_money_get = 0
    data.checks_total = proverki.get('total', 0)
    checks_plan = sum(1 for doc in proverki.get('body', []) if doc.get('@attributes').get('ITYPE_NAME') == 'Внеплановая проверка')
    checks_no_plan = sum(1 for doc in proverki.get('body', []) if doc.get('@attributes').get('ITYPE_NAME') != 'Внеплановая проверка')
    checks_violations = sum(1 for doc in proverki.get('body', []) for obj in doc.get('I_OBJECT', []) if isinstance(obj, dict) if obj.get('I_RESULT', {}) is not None and obj.get('I_RESULT', {}).get('I_VIOLATION', {}) is not None)
    checks_no_violations = sum(1 for doc in proverki.get('body', []) for obj in doc.get('I_OBJECT', []) if isinstance(obj, dict) if obj.get('I_RESULT', {}) is None or obj.get('I_RESULT', {}).get('I_VIOLATION', {}) is None)
    data.checks_plan = checks_plan
    data.checks_no_plan = checks_no_plan
    data.checks_violations = checks_violations
    data.checks_no_violations = checks_no_violations
    if len(licenses.get('items', [])) != 0:
        data.licenses = f'У {data.legal_entity_name} обнаружены сведения о {len(licenses.get("items"))} лицензиях'
    else:
        data.licenses = 'Сведения о лицензиях у организации отсутствуют.'

    fil = card.get('СвФилиал', 0)
    pred = card.get('СвПредстав', 0)
    data.filials = f'У {data.legal_entity_name} присутствует {fil + pred} филиалов и представительств.'
    reliability_success = important_facts.get('success', [])
    reliability_warning = important_facts.get('warning', [])
    reliability_danger = important_facts.get('danger', [])
    data.reliability_success = len(reliability_success)
    data.reliability_warning = len(reliability_warning)
    data.reliability_danger = len(reliability_danger)
    data.reliability_fact = len(reliability_success) + len(reliability_warning) + len(reliability_danger)
    spec_1 = card.get('НедобросовПостав', 0)
    data.spec_fns_1 = 'состоит' if spec_1 != 0 else 'не состоит'
    spec_2 = card.get('СвУчредит', {}).get('all', [])
    if len(spec_2) == 0:
        data.spec_fns_3 = 'не состоит'
    else:
        spec_fns_3 = any(spec.get('mass_leaders') != 0 for spec in spec_2 if spec.get('mass_leaders') is not None)
        data.spec_fns_3 = 'состоит' if spec_fns_3 else 'не состоит'
    founders = ''
    founders_info = card.get('СвУчредит', {}).get('all', [])
    if len(founders_info) == 0:
        data.founders = 'Данные об учредителях не найдены'
    else:
        for founder in founders_info:
            if isinstance(founder, dict):
                if founder.get("name") is not None and founder.get("dol_abs") is not None:
                    founders += f'- {founder.get("name")} (Доля: {founder.get("dol_abs")})\n'
        data.founders = founders

    return data


def format_date(date) -> str:
    return datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%d.%m.%Y')


def format_number_with_spaces(number) -> str:
    if isinstance(number, (int, float)):
        return '{:,.2f}'.format(number).replace(',', ' ').replace('.00', '')
    else:
        return str(number)


def format_money(amount) -> str:
    if isinstance(amount, (int, float)):
        suffixes = ['', 'тыс.', 'млн', 'млрд', 'трлн', 'квадр.', 'квинт.', 'секст.']
        if amount == 0:
            return '0'
        magnitude = 0
        while abs(amount) >= 1000:
            magnitude += 1
            amount /= 1000
        formatted_amount = '{:.2f}'.format(amount).rstrip('0').rstrip('.')
        return '{} {}'.format(formatted_amount, suffixes[magnitude])
    else:
        return str(amount)


def create_pdf_doc(card: Dict, fns_card: Dict, affilation_company: Dict, court_arbitration: Dict, zakupki_top: Dict, fssp_list: Dict, proverki: Dict, licenses: Dict, important_facts: Dict) -> str:
    data = data_create(
        card,
        fns_card.get('body'),
        affilation_company.get('body'),
        court_arbitration.get('body').get('точно', {}),
        zakupki_top.get('body'),
        fssp_list.get('body'),
        proverki, licenses,
        important_facts.get('body')
    )

    doc = DocxTemplate("/root/project/utils/preparation/template.docx")

    context = {
        'date': data.date,
        'legal_entity_name': data.legal_entity_name,
        'full_name': data.full_name,
        'status': data.status,
        'legal_address': data.legal_address,
        'authorized_capital': format_money(data.authorized_capital),
        'director_general': data.director_general,
        'average_headcount': data.average_headcount,
        'principal_activity_code': data.principal_activity_code,
        'principal_activity': data.principal_activity,
        'total_activities': data.total_activities,
        'ogrn': data.ogrn,
        'inn': data.inn,
        'kpp': data.kpp,
        'register_date': format_date(data.register_date),
        'registrar': data.registrar,
        'registrar_address': data.registrar_address,
        'date_registration': format_date(data.date_registration),
        'tax_authority': data.tax_authority,
        'revenue_2022': format_money(data.revenue_2022),
        'profit_2022': format_money(data.profit_2022),
        'cost_2022': format_money(data.cost_2022),
        'revenue_2021': format_money(data.revenue_2021),
        'profit_2021': format_money(data.profit_2021),
        'cost_2021': format_money(data.cost_2021),
        'revenue_2020': format_money(data.revenue_2020),
        'profit_2020': format_money(data.profit_2020),
        'cost_2020': format_money(data.cost_2020),
        'affilation_company': data.affilation_company,
        'count_court_cases': format_number_with_spaces(data.count_court_cases),
        'respondent': format_number_with_spaces(data.respondent),
        'plaintiff': format_number_with_spaces(data.plaintiff),
        'third_party': format_number_with_spaces(data.third_party),
        'claims': format_money(data.claims),
        'total_buying': format_number_with_spaces(data.total_buying),
        'money_buying': format_money(data.money_buying),
        'proceedings_total': format_number_with_spaces(data.proceedings_total),
        'proceedings_fine': format_number_with_spaces(data.proceedings_fine),
        'proceedings_no': format_number_with_spaces(data.proceedings_no),
        'proceedings_other': format_number_with_spaces(data.proceedings_other),
        'proceedings_money': format_money(data.proceedings_money),
        'proceedings_money_get': format_money(data.proceedings_money_get),
        'checks_total': format_number_with_spaces(data.checks_total),
        'checks_plan': format_number_with_spaces(data.checks_plan),
        'checks_no_plan': format_number_with_spaces(data.checks_no_plan),
        'checks_violations': format_number_with_spaces(data.checks_violations),
        'checks_no_violations': format_number_with_spaces(data.checks_no_violations),
        'licenses': data.licenses,
        'filials': data.filials,
        'reliability_fact': data.reliability_fact,
        'reliability_success': data.reliability_success,
        'reliability_warning': data.reliability_warning,
        'reliability_danger': data.reliability_danger,
        'spec_fns_1': data.spec_fns_1,
        'spec_fns_2': data.spec_fns_2,
        'spec_fns_3': data.spec_fns_3,
        'founders': data.founders
    }

    doc.render(context)
    input_path = f"/root/project/utils/preparation/temp/temp_{data.date.replace('.', '')}{data.ogrn}.docx"
    output_path = f"/root/project/utils/preparation/pdf/temp_{data.date.replace('.', '')}{data.ogrn}.pdf"
    out_dirt = '/root/project/utils/preparation/pdf'
    doc.save(input_path)

    convertapi.api_secret = 'YR8dd226sOhVo1Kg'
    convertapi.convert('pdf', {'File': input_path}, from_format='docx').save_files(out_dirt)

    return output_path
