import math
import json
import random
import string
from urllib.parse import urljoin, urlparse
import bleach
from django.conf import settings
from rest_framework import permissions

ALPHABET_SIZE = 26


def user_is_artist(user):
    if user:
        return 'Artists' in user.groups.values_list('name', flat=True)
    return False


def unit_codes(val):
    codes = []
    for code in val:
        codes.append(ord(code))
    return codes


# implement lexo ranking
def get_rank_between2(first_rank, second_rank):
    if not second_rank > first_rank:
        raise ValueError(f"secondRank must be greater than firstRank! {second_rank} is not greater than {first_rank}")
    # make positions equal
    while len(first_rank) != len(second_rank):
        if len(first_rank) > len(second_rank):
            second_rank += 'a'
        else:
            first_rank += 'a'
    first_position_codes = unit_codes(first_rank)
    second_position_codes = unit_codes(second_rank)

    difference = 0

    for index, first_code in reversed(list(enumerate(first_position_codes))):
        second_code = second_position_codes[index]
        if second_code < first_code:
            second_code += ALPHABET_SIZE
            second_position_codes[index - 1] -= 1

        # formula: x = a * size^0 + b * size^1 + c * size^2
        pow_res = math.pow(ALPHABET_SIZE, len(first_rank) - index - 1)
        difference += (second_code - first_code) * pow_res

    new_element = ''
    if difference <= 1:
        # add middle char from alphabet
        new_element = first_rank + chr(ord('a') + ALPHABET_SIZE // 2)
    else:
        difference = difference // 2
        offset = 0
        for index, first_code in enumerate(first_rank):
            # formula: x = difference / (size ^ place - 1) % size;
            # i.e.difference = 110, size = 10, we want place 2(middle),
            # then x = 100 / 10 ^ (2 - 1) % 10 = 100 / 10 % 10 = 11 % 10 = 1
            diff_in_symbols = difference // math.pow(ALPHABET_SIZE, index) % ALPHABET_SIZE
            new_element_code = ord(first_rank[len(second_rank) - index - 1]) + diff_in_symbols + offset

            # if newElement is greater then 'z'
            if new_element_code > ord('z'):
                offset += 1
                new_element_code -= ALPHABET_SIZE
            new_element += chr(int(new_element_code))

        new_element = ''.join(reversed(list(new_element)))

    return new_element


def quotient_remainder(number, divisor):
    return number // divisor, number % divisor


def to_codes(val):
    return list(map(lambda x: x - 96, unit_codes(val)))


def list_to_base_10(values):
    result = 0
    length = len(values)
    for i in range(length):
        result += values[i] * math.pow(ALPHABET_SIZE + 1, length - 1 - i)
    return int(result)


def str_to_base_10(val):
    return list_to_base_10(to_codes(val))


def to_base_26(val):
    new_chars = []
    remainder = val
    while remainder > 0:
        (quotient, num) = quotient_remainder(remainder, ALPHABET_SIZE + 1)
        new_chars.insert(0, num)
        remainder = quotient
    while 0 in new_chars:
        for i, char in enumerate(new_chars):
            if char == 0:
                if i == 0:
                    new_chars[i] = 1
                else:
                    new_chars[i] = 26
                    new_chars[i - 1] -= 1
    result = ''.join(list(map(lambda x: chr(x + 96), new_chars)))
    return result


def get_rank_between(first_rank, second_rank):
    if not second_rank > first_rank:
        raise ValueError(f"secondRank must be greater than firstRank! {second_rank} is not greater than {first_rank}")
    # make positions equal
    while len(first_rank) != len(second_rank):
        if len(first_rank) > len(second_rank):
            second_rank += 'a'
        else:
            first_rank += 'a'
    first_base_10 = str_to_base_10(first_rank)
    second_base_10 = str_to_base_10(second_rank)
    if (second_base_10 - first_base_10) <= 1:
        return first_rank + 'n'
    middle = int((first_base_10 + second_base_10) // 2)
    return to_base_26(middle)


def get_default_ranks(length):
    if length > 17576:
        raise ValueError(f"Ranks can not be generated for more than 17,576 items! {length} supplied")

    start_pos = 'aaa'
    end_pos = 'zzz'

    start_code = ord(start_pos[0])
    end_code = ord(end_pos[0])
    diff_in_one_symb = end_code - start_code

    # x = a + b * size + c * size^2
    total_diff = diff_in_one_symb + diff_in_one_symb * ALPHABET_SIZE + diff_in_one_symb * ALPHABET_SIZE * ALPHABET_SIZE
    diff_for_one_item = total_diff // (length + 1)

    # x = difference / size^(place - 1) % size
    diff_for_symbols = [
        diff_for_one_item % ALPHABET_SIZE,
        diff_for_one_item // ALPHABET_SIZE % ALPHABET_SIZE,
        diff_for_one_item // math.pow(ALPHABET_SIZE, 2) % ALPHABET_SIZE,
    ]

    positions = []
    last_added_element = start_pos

    for ind in range(length):
        offset = 0
        new_element = ''
        for index in range(3):
            diff_in_symbols = diff_for_symbols[index]
            new_element_code = ord(last_added_element[2 - index]) + diff_in_symbols
            if offset != 0:
                new_element_code += 1
                offset = 0

            if new_element_code > ord('z'):
                offset += 1
                new_element_code -= ALPHABET_SIZE

            symbol = chr(int(new_element_code))
            new_element += symbol

        # reverse element since we calculated from the end
        new_element = ''.join(reversed(list(new_element)))
        positions.append(new_element)
        last_added_element = new_element

    positions.sort()
    return positions


def json_loads(val):
    try:
        return json.loads(val)
    except ValueError:
        return val
    except TypeError:
        return None


def get_random_password(length):
    characters = string.ascii_letters + string.digits
    result_str = ''.join(random.sample(characters, length))
    return result_str


def nl2br(s):
    return '<br />\n'.join(s.split('\n'))


def get_flat_items(data, sub_key=''):
    pairs = []
    for key, val in data.items() if isinstance(data, dict) else enumerate(data):
        new_key = sub_key + '_' + str(key) if sub_key else str(key)
        if isinstance(val, (dict, list)):
            try:
                pairs = pairs + get_flat_items(val, new_key)
            except RecursionError:
                pairs.append((new_key, val))
        else:
            pairs.append((new_key, val))
    return pairs


def flatten_dict(data):
    return dict(get_flat_items(data))


def format_price(price, currency='£'):
    val = float(price)
    # if val % 1 == 0:
    #     formatted_price = '{:,.0f}'.format(val)
    # else:
    formatted_price = '{:,.2f}'.format(val)
    return currency + ' ' + formatted_price if currency else formatted_price


def custom_permission_factory(permission_name):
    """
    Create a custom permission class that checks if the user has a specific permission.

    Args:
        permission_name (str): The name of the permission to check.

    Returns:
        permissions.BasePermission: A custom permission class instance.
    """

    class CustomPermission(permissions.BasePermission):
        def has_permission(self, request, view):
            # Check if the user has the specified permission
            return request.user.has_perm(permission_name)

    return CustomPermission


def get_permission_classes(action, object_name, app_name=None):
    """
    Get permission classes based on the action and object_name.

    Args:
        action (str): The action being performed (e.g., 'list', 'retrieve', 'create', 'update', 'partial_update', 'destroy').
        object_name (str): The name of the model (e.g., 'MyModel').
        app_name (str): The name of the Django app (optional).

    Returns:
        List[permissions.BasePermission]: A list of permission class instances.
    """
    if app_name:
        permission_prefix = f"{app_name}."
    else:
        permission_prefix = ""

    # Map actions to permission names
    permission_mapping = {
        'list': 'view',
        'retrieve': 'view',
        'create': 'add',
        'update': 'change',
        'partial_update': 'change',
        'destroy': 'delete',
    }

    # Generate permission names based on the action and object_name
    permission_name = f"{permission_prefix}{permission_mapping.get(action, 'view')}_{object_name.lower()}"

    # Instantiate the permission class based on the permission name
    permission_class = custom_permission_factory(permission_name)

    return [permission_class()]


def sanitize_html(input_html):
    # Define a whitelist of allowed tags and attributes
    allowed_tags = [
        'p', 'span', 'strong', 'em', 'u', 's', 'blockquote', 'ul', 'ol', 'li', 'a', 'img'
    ]

    allowed_attributes = {
        'a': ['href', 'target', 'rel'],
        'img': ['src', 'alt'],
    }

    # Run bleach.clean with the defined whitelist
    cleaned_html = bleach.clean(
        input_html,
        tags=set(allowed_tags),
        attributes=allowed_attributes,
        strip=True,
    )

    return cleaned_html


def changed_fields(instance, validated_data):
    return [field for field, value in validated_data.items()
            if value != getattr(instance, field, None)
            and not (field == 'tags' and value == []
                     and instance.tags.count() == 0)]


def get_object_view_link(target_object, target_object_id, base_id=None):
    multi_word_objects = {
        'purchaseorder': 'purchase_order',
        'jobhub': 'job_hub',
        'jobitem': 'job_item',
    }
    obj = multi_word_objects[target_object] if target_object in multi_word_objects.keys() else target_object
    base_link = settings.FRONTEND_APP_DIR + '/app/'
    if obj == 'artwork':
        link = base_link + 'artwork/artworks/' + str(target_object_id or '')
    elif obj == 'artist':
        link = base_link + 'artwork/artists/' + str(target_object_id or '')
    elif obj == 'collection':
        link = base_link + 'artwork/collections/' + str(target_object_id or '')
    elif obj == 'collection_folder':
        link = base_link + 'artwork/collections/folder/' + str(target_object_id or '')
    elif obj == 'quotation':
        link = base_link + 'job_hub/' + str(base_id or 0) + '/quotation/' + str(target_object_id or '')
    elif obj == 'purchase_order':
        link = base_link + 'job_hub/' + str(base_id or 0) + '/purchase_order/' + str(target_object_id or '')
    elif obj == 'job_item':
        link = base_link + 'job_hub/' + str(base_id or 0) + '/item/' + str(target_object_id or '')
    elif obj == 'messaging':
        link = base_link + 'messaging' + ('?c=' + str(target_object_id) if target_object_id else '')
    else:
        link = base_link + obj + '/' + str(target_object_id or '')

    return link


def media_url(media_path, frontend=False):
    path = str(media_path).replace("\\", "/")
    if not path:
        return ''
    if path.startswith('http'):
        return path
    if frontend:
        parsed_url = urlparse(settings.FRONTEND_APP_DIR)
        origin = f"{parsed_url.scheme}://{parsed_url.netloc}"
        return urljoin(origin, path)
    base = settings.STORAGE_URL
    sas_token = settings.STORAGE_TOKEN
    return '/'.join([base.rstrip('/'), path.lstrip('/')]) + sas_token
