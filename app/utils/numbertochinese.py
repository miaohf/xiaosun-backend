
# from string to chinese 
CHINESE_NEGATIVE = '负'
CHINESE_ZERO = '零'
CHINESE_DIGITS = ['', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']
CHINESE_UNITS = ['', '拾', '佰', '仟']
CHINESE_GROUP_UNITS = ['', '万', '亿', '兆']

def _enumerate_digits(number):
    position = 0
    while number > 0:
        digit = number % 10
        number //= 10
        yield position, digit
        position += 1

def number_to_chinese_left(number):
    # if not isinstance(number, int) and not isinstance(number, float):
    if not isinstance(number, int):
        raise ValueError('number must be integer')

    if number == 0:
        return CHINESE_ZERO
    words = []
    if number < 0:
        words.append(CHINESE_NEGATIVE)
        number = -number

    group_is_zero = True
    need_zero = False
    for position, digit in reversed(list(_enumerate_digits(number))):
        unit = position % len(CHINESE_UNITS)
        group = position // len(CHINESE_UNITS)

        if digit != 0:
            if need_zero:
                words.append(CHINESE_ZERO)
            if digit != 1 or unit != 1 or not group_is_zero or (group == 0 and need_zero):
                words.append(CHINESE_DIGITS[digit])
            words.append(CHINESE_UNITS[unit])
        group_is_zero = group_is_zero and digit == 0
        if unit == 0 and not group_is_zero:
            words.append(CHINESE_GROUP_UNITS[group])
        need_zero = (digit == 0 and (unit != 0 or group_is_zero))
        if unit == 0:
            group_is_zero = True

    # End core loop.

    return ''.join(words)# Begin core loop.



DIGITS = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']

def number_to_chinese_right(number):
    jiao = DIGITS[int(number[0:1])] + '角'
    if len(number) == 2:
        fen = DIGITS[int(number[1:2])] + '分'
    else:
        fen = '零分'

    return jiao + fen

def number_to_chinese(number):
    # print('number:', number)
    # number = round(number, 2)
    left_number = int(str(number).split(".")[0])
    right_number = str(number).split(".")[1]

    print(left_number, right_number)

    left_code = number_to_chinese_left(left_number)
    if int(right_number) == 0:
        right_code = '整'
    else:
        right_code = number_to_chinese_right(right_number)


    return left_code + '圆' +  right_code