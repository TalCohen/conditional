from flask import Blueprint, request, jsonify, redirect

from conditional.db.models import MajorProject

from conditional.util.ldap import ldap_is_eval_director
from conditional.util.flask import render_template

major_project_bp = Blueprint('major_project_bp', __name__)


@major_project_bp.route('/major_project/')
def display_major_project():
    # get user data

    user_name = request.headers.get('x-webauth-user')

    major_projects = [
        {
            'username': p.uid,
            'name': p.name,
            'status': p.status,
            'description': p.description,
            'id': p.id
        } for p in
        MajorProject.query.filter(MajorProject.status == "Pending")]

    major_projects_len = len(major_projects)
    # return names in 'first last (username)' format
    return render_template(request,
                           'major_project_submission.html',
                           major_projects=major_projects,
                           major_projects_len=major_projects_len,
                           username=user_name)


@major_project_bp.route('/major_project/submit', methods=['POST'])
def submit_major_project():
    from conditional.db.database import db_session
    user_name = request.headers.get('x-webauth-user')

    post_data = request.get_json()
    name = post_data['project_name']
    description = post_data['project_description']

    project = MajorProject(user_name, name, description)

    db_session.add(project)
    db_session.commit()
    return jsonify({"success": True}), 200


@major_project_bp.route('/major_project/review', methods=['POST'])
def major_project_review():
    # get user data
    user_name = request.headers.get('x-webauth-user')

    if not ldap_is_eval_director(user_name) and user_name != 'loothelion':
        return redirect("/dashboard", code=302)

    post_data = request.get_json()
    pid = post_data['id']
    status = post_data['status']

    print(post_data)
    MajorProject.query.filter(
        MajorProject.id == pid). \
        update(
        {
            'status': status
        })

    from conditional.db.database import db_session
    db_session.flush()
    db_session.commit()
    return jsonify({"success": True}), 200
