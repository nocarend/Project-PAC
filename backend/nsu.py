from app import create_app, db
from app.models import User

# я бы пока забил на всякие хайки, ивенты
app = create_app()
app.app_context().push()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
