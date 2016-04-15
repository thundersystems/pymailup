Test
====

To run test you need the credentials obtained from your MailUp account: 'CLIENT_ID', 'CLIENT_SECRET', 'USERNAME',
'PASSWORD' and 'OWNER_EMAIL' (your email).

Test suite create a 'TEST-PYMAILUP' List where random recipient are created, subscribed, unsubscribed, etc..

To run test::

    python -m mailup --client-id CLIENT_ID --client-secret CLIENT_SECRET --username USERNAME --password PASSWORD --owner-email youremail@domain.com

if you want see log during test executing you can pass next arguments (not required)::

    --logger-enabled --log-level [NOTSET / DEBUG / INFO / WARNING  / ERROR / CRITICAL ]


