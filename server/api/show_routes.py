import json
from datetime import datetime

from flask import Blueprint, jsonify, session, request
from server.models import *
from flask_login import current_user, login_required

from server.forms.show_form import ShowCreateForm

from server.utils.awsS3 import upload_file_to_s3
from server.utils.cipher_suite import *


show_routes = Blueprint('show', __name__)


def validation_errors_to_error_messages(validation_errors):
    """
    Simple function that turns the WTForms validation errors into a simple list
    """
    errorMessages = []
    for field in validation_errors:
        for error in validation_errors[field]:
            errorMessages.append(f"{field} : {error}")
    return errorMessages


@login_required
def create_new_show():
    form = ShowCreateForm()
    form['csrf_token'].data = request.cookies['csrf_token']

    owner = current_user

    if form.validate_on_submit():

        dates = request.form['showDates']
        dates = json.loads(dates)

        if not len(dates):
            return {'errors': 'dates: No dates provided for show'}, 400



        show = Show(
            owner = owner,
            title = form.data['title'],
            description = form.data['description'],
            primary_color = form.data['primaryColor'],
            secondary_color = form.data['secondaryColor'],
            is_private = form.data['isPrivate']
        )


        for dateobj in dates:
            show_date = Show_Date(
                date = datetime.strptime(dateobj['date'], "%a, %d %b %Y %H:%M:%S %Z"),
                start_time = datetime.strptime(dateobj['startTime'], "%a, %d %b %Y %H:%M:%S %Z"),
                end_time = datetime.strptime(dateobj['endTime'], "%a, %d %b %Y %H:%M:%S %Z")
            )

            show.dates.append(show_date)

        db.session.add(show)
        db.session.commit()

        # AWS S3 Show Logo Upload

        if form.data['showLogo']:
            filename = f"shows/{show.SID}/logo.png"

            upload_file_to_s3(request.files['showLogo'], filename)
        # return ({'key': 'pass'})
        return (show.to_dict())

    return {'errors': validation_errors_to_error_messages(form.errors)}, 400


def get_public_shows():
    """
    GET - Retrieves all shows that are not marked as private as JSON
    POST - Creates a new show
    """
    public_shows = Show.query.filter_by(is_private=False).all()
    data = [show.to_dict() for show in public_shows]
    print(data)
    return jsonify(data)


@show_routes.route('/', methods=["GET", "POST"])
def show_router():
    """
    GET - Retrieves all shows that are not marked as private as JSON
    POST - Creates a new show
    """
    if request.method == "POST":
        return create_new_show()
    if request.method == "GET":
        return get_public_shows()


@show_routes.route('/my-shows/')
@login_required
def get_user_shows():
    """
    Sends shows that user is owner of as JSON
    """
    users_shows = Show.query.filter_by(owner=current_user).all()
    data = [show.to_dict() for show in public_shows]
    return jsonify(data)


@show_routes.route('/<SID>/')
@login_required
def get_show_by_SID(SID):
    id = decodeShowId(SID)
    if id:
        show = Show.query.get(id)
        if show:
            print(show.to_dict_full())
            return show.to_dict_full()
    return {'errors': ['The requested show does not exist']}, 404


@show_routes.route('/<SID>/', methods=["PUT"])
@login_required
def complete_show_update(SID):
    show_id = decodeShowId(SID)

    form = ShowCreateForm()
    form['csrf_token'].data = request.cookies['csrf_token']

    owner = current_user

    if form.validate_on_submit():

        dates = request.json['dates']
        if not dates:
            return {'errors': 'No dates provided for show'}, 400

        show = Show.query.get(show_id)

        show.owner = owner

        show.title = form.data['title'],
        show.description = form.data['description'],
        show.primary_color = form.data['primaryColor'],
        show.secondary_color = form.data['secondaryColor'],
        show.is_private = form.data['isPrivate']

        show.dates = []

        for dateobj in dates:
            show_date = Show_Date(
                date = dateobj['date'],
                start_time = dateobj['startTime'],
                end_time = dateobj['endTime']
            )
            show.dates.append(show_date)

        db.session.update(show)
        db.session.commit()

        # AWS S3 Show Logo Upload

        if form.data['showLogo']:
            filename = f"shows/{show.SID}/logo.png"

            upload_file_to_s3(request.files['showLogo'], filename)

        return jsonify(show.to_dict())

    return {'errors': validation_errors_to_error_messages(form.errors)}, 400


@show_routes.route('/<SID>/', methods=["PATCH"])
@login_required
def partial_show_update(SID):
    pass


@show_routes.route('/<SID>/', methods=["DELETE"])
@login_required
def delete_show(SID):
    pass


@show_routes.route('/<SID>/invites/', methods=["POST"])
@login_required
def create_show_invite(SID):
    pass


@show_routes.route('/<SID>/invites/<IID>/', methods=["DELETE"])
@login_required
def delete_show_invite(SID, IID):
    pass


@show_routes.route('/<SID>/partners/', methods=["POST"])
@login_required
def add_show_partner(SID):
    pass


@show_routes.route('/<SID>/partners/<userId>/', methods=["DELETE"])
@login_required
def delete_show_partner(SID, userId):
    pass


@show_routes.route('/<SID>/booths/<BID>/', methods=["GET"])
@login_required
def get_booth_info(SID, BID):
    id = decodeBoothId(BID)
    if id:
        booth = Booth.query.get(id)
        if booth:
            print(booth.to_dict_full())
            return booth.to_dict_full()
    return {'errors': ['The requested show does not exist']}, 404


@show_routes.route('/search/')
@login_required
def search_shows():
    includes = request.args.get('includes')
    excludes = request.args.get('excludes')

    # could split on spaces if multiple terms?
    includes = f"%{includes}%" if includes else ""
    excludes = f"%{excludes}%" if excludes else ""

    show_query = Show.query.filter_by(is_private=False)

    if includes:
        show_query = show_query.filter(Show.title.ilike(includes))
    if excludes:
        show_query = show_query.filter(Show.title.notilike(excludes))

    public_shows= show_query.all()

    data = [show.to_dict() for show in public_shows]
    return jsonify(data)
