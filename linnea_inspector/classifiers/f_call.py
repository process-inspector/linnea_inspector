def f_call(event):
    activity = None
    if event.call:
        activity = event.call.removeprefix("LAPACK.")
    return activity