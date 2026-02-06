# Linnea Inspector
# Copyright (c) 2021-2026 Aravind Sankaran
#
# SPDX-License-Identifier: AGPL-3.0-or-later
# See LICENSE file in the project root for full license information.

def f_call(event):
    activity = None
    if event.call:
        activity = event.call.removeprefix("LAPACK.")
    return activity