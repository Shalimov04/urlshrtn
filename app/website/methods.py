from user_agents import parse


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_device(request):
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    if 'Mobile' in user_agent or 'Android' in user_agent or 'iPhone' in user_agent:
        device_type = 'Mobile'
    elif 'iPad' in user_agent or 'Tablet' in user_agent:
        device_type = 'Tablet'
    else:
        device_type = 'Desktop'
    return device_type


def get_user_agent(request):
    user_agent_string = request.META.get('HTTP_USER_AGENT', '')
    user_agent = parse(user_agent_string)

    browser = user_agent.browser.family
    os = user_agent.os.family

    if 'Mobile' in user_agent_string or 'Android' in user_agent_string or 'iPhone' in user_agent_string:
        device_type = 'Mobile'
    elif 'iPad' in user_agent_string or 'Tablet' in user_agent_string:
        device_type = 'Tablet'
    else:
        device_type = 'Desktop'

    return {
        'browser': browser,
        'os': os,
        'device': device_type,
    }
