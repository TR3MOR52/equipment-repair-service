from prog import create_app

app = create_app()

# if __name__ == '__main__':
#     app.run(ssl_context=('prog/certs/cert.pem', 'prog/certs/key.pem'), debug=True)
if __name__ == '__main__':
    app.run(debug=True)