#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthcare_backend.settings')
    import django
    django.setup()
    from django.test.utils import get_runner
    from django.conf import settings
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2)
    failures = test_runner.run_tests([
        'auth_app.tests',
        'patients.tests',
        'doctors.tests',
        'mappings.tests',
    ])
    sys.exit(bool(failures))
