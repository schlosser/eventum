var helper = (function() {
    var authResult;

    return {
        /**
         * Hides the sign-in button and connects the server-side app after
         * the user successfully signs in.
         *
         * @param {Object} authResult An Object which contains the access token and
         *     other authentication information.
         */
        onSignInCallback: function(authResult) {
            $('#plus-button-wrapper').hide();
            if (authResult['access_token']) {
                // The user is signed in
                this.authResult = authResult;
                helper.connectServer();
                // After we load the Google+ API, render the profile data from Google+.
                gapi.client.load('plus','v1',this.renderProfile);
            } else if (authResult['error']) {
                // There was an error, which means the user is not signed in.
                // As an example, you can troubleshoot by writing to the console:
                console.log('There was an error: ' + authResult['error']);
                $('#authResult').append('Logged out');
                $('#authOps').hide('slow');
                $('#plus-button-wrapper').show();
            }
        },
        /**
         * Calls the server endpoint to connect the app for the user. The client
         * sends the one-time authorization code to the server and the server
         * exchanges the code for its own tokens to use for offline API access.
         * For more information, see:
         *     https://developers.google.com/+/web/signin/server-side-flow
         */
        connectServer: function() {
            $.ajax({
                type: 'POST',
                url: '/admin/store-token?state=' + STATE + '&next=' + NEXT,
                contentType: 'application/octet-stream; charset=utf-8',
                success: function(result) {
                    window.location.href = result;
                },
                error: function(xhr, status, err) {
                    if (xhr.status == 200) {
                        window.location.href = xhr.responseText;
                    }
                    /*
                     * Set window.error, to be parsed in displayErrors(). See
                     * below for further explination.
                     */

                    if (xhr.responseText) {
                        console.log(xhr.responseText);
                        try {
                            window.error = JSON.parse(xhr.responseText);
                        }
                        catch (ex) {
                            window.error = xhr.responseText;
                        }
                    } else {
                        console.log("Unhandled response: ", xhr);
                    }
                },
                processData: false,
                data: this.authResult.code
            });
        }
    };
})();


var WHITELIST_CODE = 1;
/**
 * Constantly be checking for window.error, and load messages.
 *
 * The Google JavaScript client library attempts to request the next page, even
 * if the server returned a 401.  Because of this, any error messages that we
 * want to display on the login page would have to exist after a failed redirect
 * (a page refresh).  Therefore, we store the error in `window.error`, and poll
 * for errors here.
 */
$(function() {
    function displayErrors() {
        if (window.error !== undefined){
            $('#plus-button-wrapper').hide();
            if (window.error.code && window.error.code == WHITELIST_CODE) {
                $('#unknown-error').addClass('hidden');
                $('#not-whitelisted').removeClass('hidden');
                $('#email').html(window.error.email);
            } else {
                $('#not-whitelisted').addClass('hidden');
                $('#unknown-error').removeClass('hidden');
                $('#error-msg').html(window.error);
            }
        } else {
            $('#plus-button-wrapper').show();
        }
        setTimeout(displayErrors, 500);
    }
    displayErrors();
});

/**
 * Calls the helper method that handles the authentication flow.
 *
 * @param {Object} authResult An Object which contains the access token and
 *     other authentication information.
 */
function onSignInCallback(authResult) {
    helper.onSignInCallback(authResult);
}
