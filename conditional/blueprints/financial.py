from flask import Blueprint
from flask import request
from flask import redirect

from conditional.util.ldap import ldap_get_room_number, ldap_get_name, ldap_get_current_students, \
    ldap_is_financial_director, ldap_set_active, ldap_is_active

from conditional.util.flask import render_template
from conditional.db.models import SpringEval

financial_bp = Blueprint('financial_bp', __name__)


@financial_bp.route('/financial')
def display_financial():
    # get user data
    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_financial_director(user_name) and user_name != 'loothelion':
        return redirect("/dashboard", code=302)

    members = [
        {
            'uid': m['uid'][0].decode('utf-8'),
            'name': ldap_get_name(m['uid'][0].decode('utf-8')),
            'onfloor': ldap_get_room_number(m['uid'][0].decode('utf-8')) != "N/A",
            'paid': "checked" if ldap_is_active(m['uid'][0].decode('utf-8')) else ""
        } for m in ldap_get_current_students()]

    # return names in 'first last (username)' format
    return render_template(request,
                           'financial.html',
                           username=user_name,
                           members=members)


@financial_bp.route('/financial/edit', methods=['POST'])
def edit_financial():
    # get user data
    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_financial_director(user_name) and user_name != 'loothelion':
        return redirect("/dashboard", code=302)

    post_data = request.get_json()
    uid = post_data['uid']
    active = post_data['active'] == "on"

    # LDAP SET VALUE
    ldap_set_active(uid, active)

    from conditional.db.database import db_session
    db_session.add(SpringEval(uid))
    db_session.flush()
    db_session.commit()
    
    return redirect("/financial", code=302)
