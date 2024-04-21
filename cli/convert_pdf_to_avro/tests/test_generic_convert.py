import pytest

from convert_pdf_to_avro.main import ProductParser


@pytest.fixture
def product_parser():
    with open('./convert_pdf_to_avro/tests/ticket.txt', 'r') as f:
        ticket_lines = f.read()
    return ticket_lines


def test_timestamp(product_parser):
    timestamp = ProductParser().get_timestamp(product_parser)
    assert timestamp == '16/03/2024 13:23'


def test_product_lines(product_parser):
    product_lines = ProductParser().get_product_lines(product_parser)
    expected_output = [
        ['1 BACALAO PUNTO SAL 589'],
        ['1 QUESO FRESCO CABRA 285'],
        ['1 PATAS DE PULPO 995'],
        ['1 NARANJA MALLA 3KG 447'],
        ['1 PATATA MALLA 2 KG 375'],
        ['1 CHAMPINON BANDEJA P 160'],
        ['1 FRESON 1 KG. 389'],
        ['1 ESP VERDE FINO 199'],
        ['1 HIGADOS POLLO 161'],
        ['1 HIGADOS POLLO 137'],
        ['1 POLLO ENTERO LIMPIO 637'],
        ['3 +PROT NATILLA VAINI 175 525'],
        ['1 12 HUEVOS CAMPEROS 262'],
        ['1 MASA DE HOJALDRE 250'],
        ['1 ATUN CLARO GIRAS PK6 420'],
        ['1 ENSALADA* 450'],
        ['1 ANACARDO NATURAL 230'],
        ['1 SAZONADOR BARBACOA 135'],
        ['2 DESOD.ROLL-ON FORMEN 215 430'],
        ['2 DEO ROLL-ON DOVE 215 430'],
        ['4 CERVEZA ESPECIAL 085 340'],
        ['1 PAN DE PUEBLO 150'],
        ['1 COCA COLA ZERO 4L 370'],
        ['PESCADO'],
        ['CABALLA'],
        ['1016 kg 395 €/kg 401'],
        ['GAMBA BLANCA MEDIANA'],
        ['0406 kg 1295 €/kg 526'],
        ['1 CALABACIN VERDE'],
        ['1556 kg 155 €/kg 241'],
        ['1 KIWI VERDE'],
        ['0484 kg 250 €/kg 121'],
        ['1 TOMATE RAMA'],
        ['1070 kg 229 €/kg 245'],
        ['1 BERENJENA'],
        ['0276 kg 189 €/kg 052'],
        ['1 PIMIENTO FREIR'],
        ['0284 kg 219 €/kg 062'],
        ['1 COLIFLOR'],
        ['1312 kg 199 €/kg 261'],
        ['1 ALCACHOFA'],
        ['0904 kg 265 €/kg 240'],
        ['1 LIMON'],
        ['0352 kg 185 €/kg 065'],
        ['1 PLATANO'],
        ['1082 kg 199 €/kg 215']
    ]

    assert product_lines == expected_output


def test_quantity_simple():
    sample_product = ['1 BACALAO PUNTO SAL 589']
    ProductParser().get_quantity(sample_product)
    assert ProductParser().product_dict['cantidad'] == 1


def test_quantity_complex():
    sample_product = ['1 12 HUEVOS CAMPEROS 262']
    ProductParser().get_quantity(sample_product)
    assert ProductParser().product_dict['cantidad'] == 1


def test_quantity_none():
    sample_product = ['3 +PROT NATILLA VAINI 175 525']
    ProductParser().get_quantity(sample_product)
    assert ProductParser().product_dict['cantidad'] == 3


def test_quantity_special_characters():
    sample_product = ['1082 kg 199 €/kg 215']
    ProductParser().get_quantity(sample_product)
    assert ProductParser().product_dict['cantidad'] == 1


def test_quantity_fish():
    sample_product = ['GAMBA BLANCA MEDIANA']
    ProductParser().get_quantity(sample_product)
    assert ProductParser().product_dict['cantidad'] == 1


def test_price_1unit():
    sample_product = ['1 BACALAO PUNTO SAL 589']
    ProductParser().get_and_convert_price(sample_product)
    assert ProductParser().product_dict['importe'] == 5.89


def test_price_fruit_fish():
    sample_product = ['0406 kg 1295 €/kg 526']
    ProductParser().get_and_convert_price(sample_product)
    assert ProductParser().product_dict['importe'] == 5.26


def test_price_none():
    sample_product = ['1 PIMIENTO FREIR']
    ProductParser().get_and_convert_price(sample_product)
    assert ProductParser().product_dict['importe'] is None


def test_price_multiple_units():
    sample_product = ['3 +PROT NATILLA VAINI 175 525']
    ProductParser().get_and_convert_price(sample_product)
    assert ProductParser().product_dict['importe'] == 5.25


def test_price_per_unit():
    sample_product = ['3 +PROT NATILLA VAINI 175 5.25']
    ProductParser().get_and_convert_price_per_unit(sample_product)
    assert ProductParser().product_dict['precio_unitario'] == 1.75


def test_price_per_unit_fruit():
    sample_product = ['1070 kg 229 €/kg 2.45']
    ProductParser().get_and_convert_price_per_unit(sample_product)
    assert ProductParser().product_dict['precio_unitario'] is None


def test_price_per_unit_none():
    sample_product = ['1 BACALAO PUNTO SAL 5.89']
    ProductParser().get_and_convert_price_per_unit(sample_product)
    assert ProductParser().product_dict['precio_unitario'] is None


def test_weight_and_variable_price():
    sample_product = ['1082 kg 199 €/kg 2.15']
    ProductParser().get_and_convert_weight_and_variable_price(sample_product)
    expected_output = (1.082, 1.99)
    output = (ProductParser().product_dict['peso'],
              ProductParser().product_dict['precio_kilitro'])
    assert output == expected_output


def test_weight_and_variable_price_none():
    sample_product = ['2 DESOD.ROLL-ON FORMEN 2.15 4.30']
    ProductParser().get_and_convert_weight_and_variable_price(sample_product)
    expected_output = (None, None)
    output = (ProductParser().product_dict['peso'],
              ProductParser().product_dict['precio_kilitro'])
    assert output == expected_output


def test_description_simple():
    sample_product = ['1 BACALAO PUNTO SAL 5.89']
    ProductParser().get_description(sample_product)
    assert ProductParser().product_dict['descripcion'] == 'BACALAO PUNTO SAL'


def test_description_number():
    sample_product = ['1 12 HUEVOS CAMPEROS 2.62']
    ProductParser().get_description(sample_product)
    assert ProductParser().product_dict['descripcion'] == '12 HUEVOS CAMPEROS'


def test_description_prefix():
    sample_product = ['3 +PROT NATILLA VAINI 1.75 5.25']
    ProductParser().get_description(sample_product)
    assert ProductParser().product_dict['descripcion'] == '+PROT NATILLA VAINI'


def test_description_suffix():
    sample_product = ['1 ENSALADA* 4.50']
    ProductParser().get_description(sample_product)
    assert ProductParser().product_dict['descripcion'] == 'ENSALADA*'


def test_description_unit():
    sample_product_list = [
        ['1 NARANJA MALLA 3KG 4.47'],
        ['1 PATATA MALLA 2 KG 3.75'],
        ['1 FRESON 1 KG. 3.89'],
        ['1 COCA COLA ZERO 4L 3.70'],
        ['1 CERVEZA 0.0% 1.50'],
        ['1 ACEITE DE OLIVA 04º HACENDADO 1L 3.99'],
    ]
    expected_output = (
        'NARANJA MALLA 3KG',
        'PATATA MALLA 2 KG',
        'FRESON 1 KG.',
        'COCA COLA ZERO 4L',
        'CERVEZA 0.0%',
        'ACEITE DE OLIVA 04º HACENDADO 1L'
    )
    output = ()
    for sample_product in sample_product_list:
        ProductParser().get_description(sample_product)
        output += (ProductParser().product_dict['descripcion'],)
    assert output == expected_output
