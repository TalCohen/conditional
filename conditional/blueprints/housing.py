from flask import Blueprint
from flask import request
from conditional.util.housing import get_queue_with_points
from conditional.util.ldap import ldap_get_onfloor_members, ldap_get_room_number, ldap_get_name
from conditional.util.flask import render_template

housing_bp = Blueprint('housing_bp', __name__)


@housing_bp.route('/housing')
def display_housing():
    # get user data

    user_name = request.headers.get('x-webauth-user')

    housing = {}
    onfloors = [uids['uid'][0].decode('utf-8') for uids in ldap_get_onfloor_members()]

    room_list = set()
    for m in onfloors:
        room = ldap_get_room_number(m)
        if room in housing:
            housing[room].append(ldap_get_name(m))
        else:
            housing[room] = [ldap_get_name(m)]
        room_list.add(room)

    # return names in 'first last (username)' format
    return render_template(request,
                           'housing.html',
                           username=user_name,
                           queue=get_queue_with_points(),
                           housing=housing,
                           room_list=sorted(list(room_list)))
