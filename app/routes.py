from flask import Blueprint, jsonify, make_response, request, abort
from app import db
from app.models.customer import Customer
from app.models.video import Video
from app.models.rental import Rental


customers_bp = Blueprint("customers_bp", __name__, url_prefix="/customers")
videos_bp = Blueprint("videos_bp", __name__, url_prefix="/videos")
rental_bp = Blueprint("rental_bp", __name__, url_prefix="/rentals")

# ----------------------------------------------------------------------------------------------------------
# -------------------------------------------- Helper Functions --------------------------------------------
# ----------------------------------------------------------------------------------------------------------


def sort_helper(cls, query, is_sort):
    atrribute = None
    sort_method = is_sort
    # Handle multiple sort attributes, use case: sort=attribute_1:asc, sort=attribute_2:asc
    sort_query_param = is_sort.split(",") if is_sort.split(",") else is_sort

    for query_param in sort_query_param:
        split_query_param = query_param.split(
            ":")  # Use case: ?sort=attribute:asc
        if len(split_query_param) == 2:
            attribute = split_query_param[0]
            sort_method = split_query_param[1]
        else:  # Client did not specify sort method
            attribute = split_query_param[0]

    return sort_attribute_helper(cls, query, attribute, sort_method)


def sort_attribute_helper(cls, query, atr=None, sort_method="asc"):
    if atr:
        if atr == "name":
            if sort_method == "desc":
                query = query.order_by(cls.name.desc())
            else:
                query = query.order_by(cls.name.asc())
        elif atr == "id":
            if sort_method == "desc":
                query = query.order_by(cls.id.desc())
            else:
                query = query.order_by(cls.id.asc())
        elif atr == "registered_at":
            if sort_method == "desc":
                query = query.order_by(cls.registered_at.desc())
            else:
                query = query.order_by(cls.registered_at.asc())
        elif atr == "postal_code":
            if sort_method == "desc":
                query = query.order_by(cls.postal_code.desc())
            else:
                query = query.order_by(cls.postal_code.asc())
        elif atr == "title":
            if sort_method == "desc":
                query = query.order_by(cls.title.desc())
            else:
                query = query.order_by(cls.title.asc())
        elif atr == "release_date":
            if sort_method == "desc":
                query = query.order_by(cls.release_date.desc())
            else:
                query = query.order_by(cls.release_date.asc())

    elif sort_method == "desc":
        query = query.order_by(cls.id.desc())
    else:
        # Sort by id in ascending order by default
        query = query.order_by(cls.id.asc())

    return query


def get_all_customer_helper(customer_list):
    customers_response = []
    for customer in customer_list:
        customers_response.append(customer.to_dict())
    return customers_response


def get_all_videos_helpers(videos_list):
    video_response = []
    for video in videos_list:
        video_response.append(
            {
                "release_date": video.Video.release_date,
                "id": video.Video.id,
                "total_inventory": video.Video.total_inventory,
                "title": video.Video.title,
                "due_date": video.due_date
            })
    return video_response


def get_all_videos_rental_customers_helper(customer_list):
    customer_response = []
    for customer in customer_list:
        customer_response.append(
            {
                "due_date": customer.due_date,
                "name": customer.Customer.name,
                "phone": customer.Customer.phone,
                "postal_code": customer.Customer.postal_code,
                "id" : customer.Customer.id
            }
        )
    return customer_response


def validate_model(cls, model_id):
    try:
        model_id = int(model_id)
    except:
        abort(make_response({"message": f"{model_id} invalid"}, 400))
    model = cls.query.get(model_id)
    if model:
        return model

    abort(make_response(
        {"message": f"{cls.__name__} {model_id} was not found"}, 404))


# ----------------------------------------------------------------------------------------------------------
# -------------------------------------------- Routes ------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------
@customers_bp.route("", methods=["GET"])
def get_all_customers():
    customer_query = Customer.query

    is_sort = request.args.get("sort")
    count_query = request.args.get("count")
    page_num_query = request.args.get("page_num")

    if is_sort:
        customer_query = sort_helper(Customer, customer_query, is_sort)
    else:
        # Sort by id in ascending order by default
        customer_query = customer_query.order_by(Customer.id.asc())

    if page_num_query and count_query and page_num_query.isnumeric() and count_query.isnumeric():
        customers = customer_query.paginate(
            page=int(page_num_query), per_page=int(count_query))
        customers_response = get_all_customer_helper(customers.items)
    elif count_query and count_query.isnumeric() and (not page_num_query or not page_num_query.isnumeric()):
        customers = customer_query.paginate(page=1, per_page=int(count_query))
        customers_response = get_all_customer_helper(customers.items)
    else:
        customers = customer_query.all()
        customers_response = get_all_customer_helper(customers)

    return make_response(jsonify(customers_response), 200)


@customers_bp.route("/<customer_id>", methods=["GET"])
def get_one_customer(customer_id):

    customer = validate_model(Customer, customer_id)

    return make_response(jsonify(customer.to_dict()), 200)


@customers_bp.route("", methods=["POST"])
def create_one_customer():
    request_body = request.get_json()
    try:
        customer = Customer(
            name=request_body["name"],
            postal_code=request_body["postal_code"],
            phone=request_body["phone"],
        )
    except KeyError as keyerror:
        abort(make_response(
            {"details": f"Request body must include {keyerror.args[0]}."}, 400))

    db.session.add(customer)
    db.session.commit()
    return make_response({"id": customer.id}, 201)


@customers_bp.route("/<customer_id>", methods=["PUT"])
def update_one_customer(customer_id):
    customer = validate_model(Customer, customer_id)
    request_body = request.get_json()
    try:
        customer.name = request_body["name"]
        customer.postal_code = request_body["postal_code"]
        customer.phone = request_body["phone"]
    except KeyError as keyerror:
        abort(make_response(
            {"details": f"Request body must include {keyerror.args[0]}."}, 400))

    db.session.commit()
    return make_response(jsonify(customer.to_dict()), 200)


@customers_bp.route("/<customer_id>", methods=["DELETE"])
def delete_one_customer(customer_id):
    customer = validate_model(Customer, customer_id)

    db.session.delete(customer)
    db.session.commit()

    return {"id": customer.id}


# --------------------------------
# ----------- VIDEOS -------------
# --------------------------------

@videos_bp.route("", methods=["GET"])
def get_all_videos():
    videos_response = []
    videos = Video.query.all()

    for video in videos:
        videos_response.append(video.to_dict())
    return make_response(jsonify(videos_response), 200)


@videos_bp.route("/<video_id>", methods=["GET"])
def get_one_video(video_id):
    video = validate_model(Video, video_id)

    return make_response(jsonify(video.to_dict()), 200)


@videos_bp.route("", methods=["POST"])
def create_one_video():
    request_body = request.get_json()
    try:
        video = Video(
            title=request_body["title"],
            release_date=request_body["release_date"],
            total_inventory=request_body["total_inventory"]
        )
    except KeyError as keyerror:
        abort(make_response(
            {"details": f"Request body must include {keyerror.args[0]}."}, 400))

    db.session.add(video)
    db.session.commit()

    return make_response({"id": video.id, "title": video.title, "total_inventory": video.total_inventory}, 201)


@videos_bp.route("/<video_id>", methods=["PUT"])
def update_one_video(video_id):
    video = validate_model(Video, video_id)
    request_body = request.get_json()
    try:
        video.title = request_body["title"]
        video.release_date = request_body["release_date"]
        video.total_inventory = request_body["total_inventory"]
    except KeyError as keyerror:
        abort(make_response(
            {"details": f"Request body must include {keyerror.args[0]}."}, 400))

    db.session.commit()

    return make_response(jsonify(video.to_dict()), 200)


@videos_bp.route("/<video_id>", methods=["DELETE"])
def delete_one_video(video_id):
    video = validate_model(Video, video_id)

    db.session.delete(video)
    db.session.commit()

    return {"id": video.id}


# --------------------------------
# ----------- Rentals -------------
# --------------------------------

@rental_bp.route("/check-out", methods=["POST"])
def checkout_one_video():
    request_body = request.get_json()

    try:
        customer = validate_model(Customer, request_body["customer_id"])
        video = validate_model(Video, request_body["video_id"])

        # avaliable inventory = total inventory - total checkedout
        available_to_rent = video.total_inventory - \
            Rental.query.filter_by(video_id=video.id).count()
        if available_to_rent < 1:
            abort(make_response(
                {"message": "Could not perform checkout"}, 400))

        # update customer database
        customer.videos_checked_out_count += 1

        new_rental = Rental(
            customer_id=customer.id,
            video_id=video.id,
            videos_checked_out_count=customer.videos_checked_out_count,
            # Decrement current available_inventory
            available_inventory=available_to_rent - 1
        )
    except KeyError as keyerror:
        abort(make_response(
            {"details": f"Request body must include {keyerror.args[0]}."}, 400))

    db.session.add(new_rental)
    db.session.commit()

    return make_response(jsonify(new_rental.to_dict()), 200)


@rental_bp.route("/check-in", methods=["POST"])
def check_in_one_video():
    request_body = request.get_json()

    try:
        customer = validate_model(Customer, request_body["customer_id"])
        video = validate_model(Video, request_body["video_id"])

        # Decrement customer's videos checked out count when they return the video
        customer.videos_checked_out_count -= 1
        # Increment inventory when video is returned
        available_inventory = video.total_inventory - \
            Rental.query.filter_by(video_id=video.id).count() + 1
        # find the rental record that needs to be deleted
        to_delete_rental = Rental.query.filter_by(
            video_id=video.id, customer_id=customer.id).first()

        if to_delete_rental:
            db.session.delete(to_delete_rental)
            db.session.commit()
        else:
            abort(make_response(
                {"message": f"No outstanding rentals for customer {customer.id} and video {video.id}"}, 400))

    except KeyError as keyerror:
        abort(make_response(
            {"details": f"Request body must include {keyerror.args[0]}."}, 400))

    return {
        "customer_id": customer.id,
        "video_id": video.id,
        "videos_checked_out_count": customer.videos_checked_out_count,
        "available_inventory": available_inventory
    }, 200


@customers_bp.route("<id>/rentals", methods=["GET"])
# List the videos a customer currently has checked out
def videos_customer_checked_out(id):
    customer = validate_model(Customer, id)

    is_sort = request.args.get("sort")
    count_query = request.args.get("count")
    page_num_query = request.args.get("page_num")

    join_query = db.session.query(Video, Rental.due_date).join(
        Rental).filter(Rental.customer_id == customer.id)

    if is_sort:
        join_query = sort_helper(Video, join_query, is_sort)
    else:
        # Sort by id in ascending order by default
        join_query = join_query.order_by(Video.id.asc())

    if page_num_query and count_query and page_num_query.isnumeric() and count_query.isnumeric():
        join_query = join_query.paginate(
            page=int(page_num_query), per_page=int(count_query))
        videos_response = get_all_videos_helpers(join_query.items)
    elif count_query and count_query.isnumeric() and (not page_num_query or not page_num_query.isnumeric()):
        join_query = join_query.paginate(page=1, per_page=int(count_query))
        videos_response = get_all_videos_helpers(join_query.items)
    else:
        join_query = join_query.all()
        print(join_query)
        videos_response = get_all_videos_helpers(join_query)

    return make_response(jsonify(videos_response), 200)


@videos_bp.route("<id>/rentals", methods=["GET"])
# List the customers who currently have the video checked out
def customers_have_the_video_checked_out(id):
    video = validate_model(Video, id)

    is_sort = request.args.get("sort")
    count_query = request.args.get("count")
    page_num_query = request.args.get("page_num")

    join_query = db.session.query(Customer, Rental.due_date).join(
        Rental).filter(Rental.video_id == video.id)
    if is_sort:
        join_query = sort_helper(Customer, join_query, is_sort)
    else:
        # Sort by id in ascending order by default
        join_query = join_query.order_by(Customer.id.asc())

    if page_num_query and count_query and page_num_query.isnumeric() and count_query.isnumeric():
        join_query = join_query.paginate(
            page=int(page_num_query), per_page=int(count_query))
        customer_response = get_all_videos_rental_customers_helper(
            join_query.items)
    elif count_query and count_query.isnumeric() and (not page_num_query or not page_num_query.isnumeric()):
        join_query = join_query.paginate(page=1, per_page=int(count_query))
        customer_response = get_all_videos_rental_customers_helper(
            join_query.items)
    else:
        join_query = join_query.all()
        print(type(join_query))
        customer_response = get_all_videos_rental_customers_helper(join_query)

    return make_response(jsonify(customer_response), 200)
