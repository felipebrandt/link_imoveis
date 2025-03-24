

def get_pagination_data(model, offset, limit):
    return model.select().order_by(model.property_id).offset(offset).limit(limit)


def generate_pagination_urls(base_url, current_page, total_pages):
    urls = {}
    if current_page > 1:
        urls['previous'] = f"{base_url}?page={current_page - 1}"
    if current_page < total_pages:
        urls['next'] = f"{base_url}?page={current_page + 1}"
    return urls
