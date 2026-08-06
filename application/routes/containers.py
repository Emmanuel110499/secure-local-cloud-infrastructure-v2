from datetime import datetime

from flask import (
    Blueprint,
    current_app,
    jsonify,
    render_template,
    session,
)

from decorators import login_required


containers_bp = Blueprint(
    "containers",
    __name__,
)


@containers_bp.route("/containers")
@login_required
def containers_page():
    docker_service = current_app.extensions[
        "docker_service"
    ]

    return render_template(
        "containers.html",
        containers=docker_service.list_containers(),
    )


@containers_bp.route("/images")
@login_required
def images_page():
    docker_service = current_app.extensions[
        "docker_service"
    ]

    return render_template(
        "images.html",
        images=docker_service.list_images(),
    )


@containers_bp.route("/volumes")
@login_required
def volumes_page():
    docker_service = current_app.extensions[
        "docker_service"
    ]

    return render_template(
        "volumes.html",
        volumes=docker_service.list_volumes(),
    )


@containers_bp.route("/networks")
@login_required
def networks_page():
    docker_service = current_app.extensions[
        "docker_service"
    ]

    return render_template(
        "networks.html",
        networks=docker_service.list_networks(),
    )


@containers_bp.route("/api/docker/containers")
@login_required
def api_docker_containers():
    docker_service = current_app.extensions[
        "docker_service"
    ]

    containers = docker_service.list_containers()

    return jsonify({
        "count": len(containers),
        "containers": containers,
        "updated_at": datetime.now().isoformat(),
    })


@containers_bp.route("/api/docker/images")
@login_required
def api_docker_images():
    docker_service = current_app.extensions[
        "docker_service"
    ]

    images = docker_service.list_images()

    return jsonify({
        "count": len(images),
        "images": images,
        "updated_at": datetime.now().isoformat(),
    })


@containers_bp.route("/api/docker/volumes")
@login_required
def api_docker_volumes():
    docker_service = current_app.extensions[
        "docker_service"
    ]

    volumes = docker_service.list_volumes()

    return jsonify({
        "count": len(volumes),
        "volumes": volumes,
        "updated_at": datetime.now().isoformat(),
    })


@containers_bp.route("/api/docker/networks")
@login_required
def api_docker_networks():
    docker_service = current_app.extensions[
        "docker_service"
    ]

    networks = docker_service.list_networks()

    return jsonify({
        "count": len(networks),
        "networks": networks,
        "updated_at": datetime.now().isoformat(),
    })


@containers_bp.route(
    "/api/docker/<container_name>/<action>",
    methods=["POST"],
)
@login_required
def docker_container_action(
    container_name: str,
    action: str,
):
    docker_service = current_app.extensions[
        "docker_service"
    ]

    audit_service = current_app.extensions[
        "audit_service"
    ]

    payload, status_code = docker_service.execute_action(
        container_name,
        action,
    )

    audit_service.record_action(
        user=session.get(
            "username",
            "inconnu",
        ),
        resource=container_name,
        action=action,
        success=(status_code == 200),
        details=payload.get(
            "error",
            payload.get(
                "status",
                "",
            ),
        ),
    )

    return jsonify(payload), status_code


@containers_bp.route(
    "/api/docker/<container_name>/logs",
)
@login_required
def docker_container_logs(
    container_name: str,
):
    docker_service = current_app.extensions[
        "docker_service"
    ]

    payload, status_code = docker_service.get_logs(
        container_name,
    )

    return jsonify(payload), status_code