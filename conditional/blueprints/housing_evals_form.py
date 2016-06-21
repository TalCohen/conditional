from flask import Blueprint
from flask import request
from flask import jsonify

from conditional.db.models import HousingEvalsSubmission, EvalSettings
from conditional.util.flask import render_template

housing_evals_form_bp = Blueprint('housing_evals_form_bp', __name__)


@housing_evals_form_bp.route('/housing_evals_form/')
def display_housing_evals_form():
    # get user data

    user_name = request.headers.get('x-webauth-user')

    eval_data = HousingEvalsSubmission.query.filter(
        HousingEvalsSubmission.uid == user_name).first()

    if HousingEvalsSubmission.query.filter(
                    HousingEvalsSubmission.uid == user_name).count() > 0:
        eval_data = {
            'social_attended': eval_data.social_attended,
            'social_hosted': eval_data.social_hosted,
            'seminars_attended': eval_data.technical_attended,
            'seminars_hosted': eval_data.technical_hosted,
            'projects': eval_data.projects,
            'comments': eval_data.comments
        }

    is_open = EvalSettings.query.first().housing_form_active

    # return names in 'first last (username)' format
    return render_template(request,
                           'housing_evals_form.html',
                           username=user_name,
                           eval_data=eval_data,
                           is_open=is_open)


@housing_evals_form_bp.route('/housing_evals/submit', methods=['POST'])
def display_housing_evals_submit_form():
    from conditional.db.database import db_session
    user_name = request.headers.get('x-webauth-user')

    post_data = request.get_json()
    social_attended = post_data['social_attended']
    social_hosted = post_data['social_hosted']
    seminars_attended = post_data['seminars_attended']
    seminars_hosted = post_data['seminars_hosted']
    projects = post_data['projects']
    comments = post_data['comments']

    if HousingEvalsSubmission.query.filter(
                    HousingEvalsSubmission.uid == user_name).count() > 0:
        HousingEvalsSubmission.query.filter(
            HousingEvalsSubmission.uid == user_name). \
            update(
            {
                'social_attended': social_attended,
                'social_hosted': social_hosted,
                'technical_attended': seminars_attended,
                'technical_hosted': seminars_hosted,
                'projects': projects,
                'comments': comments
            })
    else:
        heval = HousingEvalsSubmission(user_name, social_attended,
                                       social_hosted, seminars_attended, seminars_hosted,
                                       projects, comments)

        db_session.add(heval)
    db_session.commit()
    return jsonify({"success": True}), 200
