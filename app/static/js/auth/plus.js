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
            $('#gSignInWrapper').hide();
            $('#authResult').html('Auth Result:<br/>');
            for (var field in authResult) {
                $('#authResult').append(' ' + field + ': ' + authResult[field] + '<br/>');
            }
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
                $('#gSignInWrapper').show();
            }
            console.log('authResult', authResult);
        },
        /**
         * Calls the server endpoint to connect the app for the user. The client
         * sends the one-time authorization code to the server and the server
         * exchanges the code for its own tokens to use for offline API access.
         * For more information, see:
         *     https://developers.google.com/+/web/signin/server-side-flow
         */
        connectServer: function() {
            console.log(this.authResult.code);
            $.ajax({
                type: 'POST',
                url: '/store-token?state=' + STATE + '&next=' + NEXT,
                contentType: 'application/octet-stream; charset=utf-8',
                success: function(result) {
                    console.log(result);
                    window.location.href = result;
                },
                processData: false,
                data: this.authResult.code
            });
        }
    };
})();

/**
 * Calls the helper method that handles the authentication flow.
 *
 * @param {Object} authResult An Object which contains the access token and
 *     other authentication information.
 */
function onSignInCallback(authResult) {
    helper.onSignInCallback(authResult);
}