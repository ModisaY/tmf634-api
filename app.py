from flask import Flask, request, jsonify, abort
from flask_pymongo import PyMongo
from datetime import datetime
import uuid
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "TMF634 API is running!"

app.config["MONGO_URI"] = "mongodb+srv://tmf634:Tmf634_Modisa@tm-forum.7n7clfv.mongodb.net/tmf634?retryWrites=true&w=majority&appName=TM-Forum"
mongo = PyMongo(app)

def now_iso():
    return datetime.utcnow().isoformat() + "Z"
    
# ResourceCatalog Endpoints
@app.route("/resourceCatalog", methods=["POST"])
def create_resource_catalog():
    data = request.json
    catalog_id = str(uuid.uuid4().int)[:4]
    catalog = {
        "id": catalog_id,
        "href": f"https://mycsp.com:8080/tmf-api/resourceCatalog/v5/resourceCatalog/{catalog_id}",
        "name": data["name"],
        "description": data.get("description", ""),
        "@type": data.get("@type", "ResourceCatalog"),
        "lastUpdate": now_iso(),
        "lifecycleStatus": "Tentative"
    }
    mongo.db.resourceCatalogs.insert_one(catalog)
    return jsonify(catalog), 201

@app.route("/resourceCatalog", methods=["GET"])
def list_resource_catalogs():
    catalogs = list(mongo.db.resourceCatalogs.find({}, {'_id': False}))
    return jsonify(catalogs), 200

@app.route("/resourceCatalog/<catalog_id>", methods=["GET"])
def get_resource_catalog(catalog_id):
    catalog = mongo.db.resourceCatalogs.find_one({"id": catalog_id}, {'_id': False})
    if not catalog:
        abort(404)
    return jsonify(catalog), 200

@app.route("/resourceCatalog/<catalog_id>", methods=["PATCH"])
def update_resource_catalog(catalog_id):
    updates = request.json
    result = mongo.db.resourceCatalogs.update_one({"id": catalog_id}, {"$set": updates})
    if result.matched_count == 0:
        abort(404)
    catalog = mongo.db.resourceCatalogs.find_one({"id": catalog_id}, {'_id': False})
    return jsonify(catalog), 200

@app.route("/resourceCatalog/<catalog_id>", methods=["DELETE"])
def delete_resource_catalog(catalog_id):
    result = mongo.db.resourceCatalogs.delete_one({"id": catalog_id})
    if result.deleted_count == 0:
        abort(404)
    return "", 204

# ImportJob Endpoints

@app.route("/importJob", methods=["POST"])
def create_import_job():
    data = request.json
    job_id = str(uuid.uuid4().int)[:4]
    job = {
        "id": job_id,
        "href": f"https://mycsp.com:8080/tmf-api/resourceCatalog/v5/importJob/{job_id}",
        "contentType": data.get("contentType", "application/json"),
        "creationDate": now_iso(),
        "path": data.get("path"),
        "status": "Running",
        "url": data["url"],
        "errorLog": "http://my-platform/logging/errors.log",
        "@type": data.get("@type", "ImportJob")
    }
    mongo.db.importJobs.insert_one(job)
    return jsonify(job), 201

@app.route("/importJob", methods=["GET"])
def list_import_jobs():
    creation_date = request.args.get("creationDate")
    if creation_date:
        jobs = list(mongo.db.importJobs.find({"creationDate": {"$regex": f"^{creation_date}"}}, {'_id': False}))
        return jsonify(jobs), 200
    jobs = list(mongo.db.importJobs.find({}, {'_id': False}))
    return jsonify(jobs), 200

@app.route("/importJob/<job_id>", methods=["GET"])
def get_import_job(job_id):
    job = mongo.db.importJobs.find_one({"id": job_id}, {'_id': False})
    if not job:
        abort(404)
    return jsonify(job), 200

@app.route("/importJob/<job_id>", methods=["DELETE"])
def delete_import_job(job_id):
    result = mongo.db.importJobs.delete_one({"id": job_id})
    if result.deleted_count == 0:
        abort(404)
    return "", 204

# ResourceSpecification Endpoints

@app.route("/resourceSpecification", methods=["POST"], strict_slashes=False)
def create_resource_spec():
    try:
        data = request.json
        spec_id = str(uuid.uuid4().int)[:4]

        intent_spec = data.get("intentSpecification", {})
        if not isinstance(intent_spec, dict):
            intent_spec = {}

        intent_spec.setdefault("@type", "IntentSpecificationRef")
        intent_spec.setdefault("id", "intent-id")
        intent_spec.setdefault("href", "https://example.com/tmf-api/intent/v5/intentSpecification/intent-id")
        intent_spec.setdefault("name", "Default Intent Spec")
        intent_spec.setdefault("@referredType", "IntentSpecification")

        resource_spec = {
            "id": spec_id,
            "href": f"https://mycsp.com:8080/tmf-api/resourceCatalog/v5/resourceSpecification/{spec_id}",
            "name": data["name"],
            "description": data.get("description", ""),
            "@type": data.get("@type", "ResourceSpecification"),
            "@schemaLocation": data.get("@schemaLocation", ""),
            "version": data.get("version", "1.0"),
            "validFor": data.get("validFor", {}),
            "lastUpdate": now_iso(),
            "lifecycleStatus": data.get("lifecycleStatus", "Tentative"),
            "isBundle": data.get("isBundle", False),
            "category": data.get("category", ""),
            "attachment": data.get("attachment", []),
            "relatedParty": data.get("relatedParty", []),
            "resourceSpecCharacteristic": data.get("resourceSpecCharacteristic", []),
            "resourceSpecRelationship": data.get("resourceSpecRelationship", []),
            "targetResourceSchema": data.get("targetResourceSchema", {}),
            "intentSpecification": intent_spec
        }

        mongo.db.resourceSpecifications.insert_one(resource_spec)
        return jsonify(resource_spec), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/resourceSpecification", methods=["GET"], strict_slashes=False)
def list_resource_specs():
    specs = list(mongo.db.resourceSpecifications.find({}, {'_id': False}))
    return jsonify(specs), 200

@app.route("/resourceSpecification/<spec_id>", methods=["GET"], strict_slashes=False)
def get_resource_spec(spec_id):
    spec = mongo.db.resourceSpecifications.find_one({"id": spec_id}, {'_id': False})
    if not spec:
        abort(404)
    return jsonify(spec), 200

@app.route("/resourceSpecification/<spec_id>", methods=["PATCH"], strict_slashes=False)
def update_resource_spec(spec_id):
    updates = request.json
    result = mongo.db.resourceSpecifications.update_one({"id": spec_id}, {"$set": updates})
    if result.matched_count == 0:
        abort(404)
    spec = mongo.db.resourceSpecifications.find_one({"id": spec_id}, {'_id': False})
    spec["lastUpdate"] = now_iso()
    return jsonify(spec), 200

@app.route("/resourceSpecification/<spec_id>", methods=["DELETE"], strict_slashes=False)
def delete_resource_spec(spec_id):
    result = mongo.db.resourceSpecifications.delete_one({"id": spec_id})
    if result.deleted_count == 0:
        abort(404)
    return "", 204

@app.route("/", methods=["GET"])
def home():
    return "TMF634 API is running!"

if __name__ == "__main__":
    app.run(port=5000)
