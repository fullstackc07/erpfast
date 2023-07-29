ruComplex = [
    'ч',  'ш',  'ю', 'ц', 'я', 'ў', 'ў', 'ғ', 'ғ', 'е', 'ё',
    'Ч',  'Ш',  'Ю', 'Ц', 'Я', 'Ў', 'Ў', 'Ғ', 'Ғ', 'Е', 'Ё',
]

uzComplex = [
    'ch', 'sh',  'yu', 'ts', 'ya', 'o`', "o'", 'g`', "o`",  'ye', 'yo',
    'Ch', 'Sh',  'Yu', 'Ts', 'Ya', 'O`', "O'", 'G`', "O`",  'Ye', 'Yo',
]

ruSimple = [
    'ж',  'а', 'б', 'в', 'г', 'д',  'з', 'и', 'й', 'к', 'л', 'м',
    'н', 'о', 'п', 'қ', 'р', 'с', 'т', 'у', 'ф', 'х', 'ҳ',
    'Ж',  'А', 'Б', 'В', 'Г', 'Д',  'З', 'И', 'Й', 'К', 'Л', 'М',
    'Н', 'О', 'П', 'Қ', 'Р', 'С', 'Т', 'У', 'Ф', 'Х', 'Ҳ', 'ъ', "ъ",
]

uzSimple = [
    'j',  'a', 'b', 'v', 'g', 'd', 'z', 'i', 'y', 'k', 'l', 'm',
    'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'f', 'x', 'h',
    'J',  'A', 'B', 'V', 'G', 'D', 'Z', 'I', 'Y', 'K', 'L', 'M',
    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'F', 'X', 'H',  '`', "'",
]


def tarjima(statement: str, to_form: str):
    
    if to_form not in ['uz', 'ru']:
        raise ValueError("to_form argument has to be in form of `uz` or `ru`")
    

    if to_form == 'uz':
        
        # first of all, complex letters are converted

        for ru, uz in zip(ruComplex, uzComplex):
            statement = statement.replace(ru, uz)

        # next, simple letters are converted

        for ru, uz in zip(ruSimple, uzSimple):
            statement = statement.replace(ru, uz)

    else:

        # first of all, complex letters are converted

        for uz, ru in zip(uzComplex, ruComplex):
            statement = statement.replace(uz, ru)

        # next, simple letters are converted

        for uz, ru in zip(uzSimple, ruSimple):
            statement = statement.replace(uz, ru)


    return statement
