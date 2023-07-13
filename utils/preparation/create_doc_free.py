import datetime
import logging

import convertapi
from docxtpl import DocxTemplate
from types import SimpleNamespace
from typing import Dict


def check_nonetype(data) -> str:
    return data if data is not None else 'Нет данных'


def data_create(card: Dict, fns_card: Dict, court_arbitration: Dict, zakupki_top: Dict,
                fssp_list: Dict, proverki: Dict) -> SimpleNamespace:
    data = SimpleNamespace()

    data.date = check_nonetype(datetime.datetime.now().strftime('%d.%m.%Y'))
    data.legal_entity_name = check_nonetype(card.get('НаимЮЛСокр', 'Нет данных'))
    data.full_name = check_nonetype(card.get('НаимЮЛПолн', 'Нет данных'))

    data.status = 'Доступно в платной версии'
    data.legal_address = check_nonetype(card.get('Адрес', 'Нет данных'))
    data.authorized_capital = 'Доступно в платной версии'
    data.director_general = 'Доступно в платной версии'
    data.spec_fns_2 = 'Доступно в платной версии'
    data.average_headcount = 'Доступно в платной версии'
    data.principal_activity_code = check_nonetype(card.get('КодОКВЭД', 'Нет данных'))
    data.principal_activity = check_nonetype(card.get('НаимОКВЭД', 'Нет данных'))
    data.total_activities = 'Доступно в платной версии'
    data.ogrn = check_nonetype(card.get('ОГРН', 'Нет данных'))
    data.inn = check_nonetype(card.get('ИНН', 'Нет данных'))
    data.kpp = check_nonetype(card.get('КПП', 'Нет данных'))
    data.register_date = 'Доступно в платной версии'
    data.registrar = 'Доступно в платной версии'
    data.registrar_address = check_nonetype(fns_card.get('СвРегОрг', {}).get('@attributes', {}).get('АдрРО', 'Нет данных'))
    data.date_registration = check_nonetype(fns_card.get('СвУчетНО', {}).get('@attributes', {}).get('ДатаПостУч', 'Нет данных'))
    data.tax_authority = 'Доступно в платной версии'
    data.revenue_2022 = 'Доступно в платной версии'
    data.profit_2022 = 'Доступно в платной версии'
    data.cost_2022 = 'Доступно в платной версии'
    data.revenue_2021 = 'Доступно в платной версии'
    data.profit_2021 = 'Доступно в платной версии'
    data.cost_2021 = 'Доступно в платной версии'
    data.revenue_2020 = check_nonetype(card.get('ФО2020', {}).get('ВЫРУЧКА', 'Нет данных'))
    data.profit_2020 = check_nonetype(card.get('ФО2020', {}).get('ПРИБЫЛЬ', 'Нет данных'))
    data.cost_2020 = check_nonetype(card.get('ФО2020', {}).get('ОСНСРЕДСТВА', 'Нет данных'))
    data.affilation_company = 'Доступно в платной версии'
    data.count_court_cases = court_arbitration.get('всего', 0)
    data.respondent = 'Доступно в платной версии'
    data.plaintiff = 'Доступно в платной версии'
    data.claims = 'Доступно в платной версии'
    data.third_party = 'Доступно в платной версии'
    total_buying = zakupki_top.get('total', 0)
    data.total_buying = total_buying
    data.money_buying = 'Доступно в платной версии'
    try:
        data.proceedings_total = fssp_list.get('total', 0)
    except AttributeError:
        data.proceedings_total = 0
    data.proceedings_fine = 'Доступно в платной версии'
    data.proceedings_no = 'Доступно в платной версии'
    data.proceedings_other = 'Доступно в платной версии'
    data.proceedings_money = 'Доступно в платной версии'
    data.proceedings_money_get = 'Доступно в платной версии'
    data.checks_total = proverki.get('total', 0)
    data.checks_plan = 'Доступно в платной версии'
    data.checks_no_plan = 'Доступно в платной версии'
    data.checks_violations = 'Доступно в платной версии'
    data.checks_no_violations = 'Доступно в платной версии'
    data.licenses = 'Доступно в платной версии'

    fil = card.get('СвФилиал', 0)
    pred = card.get('СвПредстав', 0)
    data.filials = f'У {data.legal_entity_name} присутствует {fil + pred} филиалов и представительств.'
    data.reliability_success = 'Доступно в платной версии'
    data.reliability_warning = 'Доступно в платной версии'
    data.reliability_danger = 'Доступно в платной версии'
    data.reliability_fact = 'Доступно в платной версии'
    data.spec_fns_1 = 'Доступно в платной версии'
    data.spec_fns_3 = 'Доступно в платной версии'
    data.founders = 'Доступно в платной версии'

    return data


def format_date(date) -> str:
    try:
        return datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%d.%m.%Y')
    except Exception:
        return date


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


def create_pdf_doc_free(card: Dict, fns_card: Dict, proverki: Dict, court_arbitration: Dict, zakupki_top: Dict, fssp_list: Dict) -> str:
    data = data_create(
        card,
        fns_card.get('body'),
        court_arbitration.get('body').get('точно', {}),
        zakupki_top.get('body'),
        fssp_list.get('body'),
        proverki
    )

    doc = DocxTemplate("/root/project/utils/preparation/template_free.docx")

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
    input_path = f"/root/project/utils/preparation/temp/temp_free_{data.date.replace('.', '')}{data.ogrn}.docx"
    output_path = f"/root/project/utils/preparation/pdf/temp_free_{data.date.replace('.', '')}{data.ogrn}.pdf"
    out_dirt = '/root/project/utils/preparation/pdf'
    doc.save(input_path)

    convertapi.api_secret = 'YR8dd226sOhVo1Kg'
    convertapi.convert('pdf', {'File': input_path}, from_format='docx').save_files(out_dirt)

    return output_path
