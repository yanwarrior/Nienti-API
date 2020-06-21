def generate_number(object_model, prefix='PRD'):
    if not object_model.objects.all().last():
        counter = 1
    else:
        counter = object_model.objects.all().last().pk + 1
    return f'{prefix}-{"%04d" % counter}'

