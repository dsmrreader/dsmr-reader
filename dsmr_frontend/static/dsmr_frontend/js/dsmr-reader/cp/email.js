var GMAIL_HOST = "aspmx.l.google.com";
var mode = null;


$(document).ready(function () {
    $('[data-action="test"]').click(function () {
        send_test_email();
    });
    $('[data-action="save"]').click(function () {
        save();
    });

    sync()

    if ($("#host").val() == GMAIL_HOST) {
        mode = "gmail"
        render_mode()
    }
});

function sync() {
    client.action(schema, ['settings', 'email', 'read']).then(function (result) {
        $("#email_to").val(result.email_to)
        $("#host").val(result.host)
        $("#port").val(result.port)
        $("#username").val(result.username)
        $("#password").val(result.password)

        if (result.use_tls) {
            $("#use_tls").attr("checked", "checked")
        } else {
            $("#use_tls").attr("checked", "")
        }

        if (result.use_ssl) {
            $("#use_ssl").attr("checked", "checked")
        } else {
            $("#use_ssl").attr("checked", "")
        }
    })
}

function send_test_email() {
    client.action(schema, ['settings', 'email', 'test', 'create']
    ).then(function (result) {
        $("#messages").html(result.message)
    }).catch(function (error) {
        console.error(error)
        $("#messages").html(error)
    })
}

function render_mode() {
    if (!mode) {

    } else if (mode == "gmail") {
        $('[data-gui="email-address"]').removeClass("hidden")
        $('[data-gui="controls"]').removeClass("hidden")
    } else {

    }
}

function save() {
    if (mode == "gmail") {
        apply_gmail($("#email_to").val())
    } else {

    }
}

function apply_gmail(email) {
    if (!email.endsWith("@gmail.com")) {
        return
    }

    client.action(schema, ['settings', 'email', 'update'], {
        "email_to": email,
        "host": GMAIL_HOST,
        "port": 25,
        "username": null,
        "password": null,
        "use_tls": true,
        "use_ssl": false,
    }).then(function (result) {
        console.info(result);
        $("#messages").html('OK')
    }).catch(function (error) {
        console.error(error);
        $("#messages").html(error)
    })

}