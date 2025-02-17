gemini_regions = [
    "asia-east1", "asia-east2", "asia-northeast1", "asia-northeast3", "asia-south1",
    "asia-southeast1", "australia-southeast1", "europe-central2", "europe-north1",
    "europe-southwest1", "europe-west1", "europe-west2", "europe-west3",
    "europe-west4", "europe-west6", "europe-west8", "europe-west9", "me-west1", "northamerica-northeast1",
    "southamerica-east1",
    "us-central1", "us-east1", "us-east4", "us-south1", "us-west1",
    "us-west4"
]
model_regions = {
    "gemini-1.5-pro-preview-0514": gemini_regions,
    "gemini-1.5-flash-preview-0514": gemini_regions,
    "gemini-1.0-pro-002": gemini_regions,
    "gemini-1.0-pro-vision-001": gemini_regions,
    "claude-3-opus@20240229": ["us-east5"],
    "claude-3-sonnet@20240229": ["asia-southeast1", "us-central1"], #"europe-west4", 
    "claude-3-haiku@20240307": ["us-central1"], #"europe-west4",  "asia-southeast1", 
    "claude-3-5-sonnet@20240620": ["us-east5"],#"europe-west1", "us-east5"],
    "mistral-large": ["europe-west4", "us-central1"],
    "mistral-nemo": ["europe-west4", "us-central1"],
    "jamba-1.5-mini": ["us-central1", "europe-west4"],
    "jamba-1.5-large": ["us-central1"],
    "meta-llama3-405b-instruct-maas": ["us-central1"],
    "meta-llama3-70b-instruct-maas": ["us-central1"],
    "meta-llama3-8b-instruct-maas": ["us-central1"],
}
