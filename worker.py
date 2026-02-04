import redis
import json
from router import EmailClassificationResponse, EmailRequest
from model import SpamDetectionModel
import numpy as np

clf_model = SpamDetectionModel(from_file=True, filepath="spam.pkl")
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
def batch_process_worker():
    while True:
        email_id = r.brpoplpush("classify_queue", "in_progress", timeout=0)
        try:
            email_json = r.get(email_id)
            if not email_json:
                r.lrem("in_progress", 1, email_id)
                continue
            email_req = EmailRequest.model_validate_json(email_json)
            model_input = clf_model.transform(np.array([str(email_req)]))

            probs = clf_model.predict_proba(model_input)
            tier = clf_model.assign_tier_score(probs[:, 1], 0.3, 0.6)
            spam_prob = float(probs[:, 1][0])
            response = EmailClassificationResponse(email_id=email_id, score=spam_prob, tier=tier[0])
            with r.pipeline() as pipe:
                pipe.set(f"result:{email_id}", response.model_dump_json())
                pipe.lrem("in_progress", 1, email_id)
                pipe.execute()
                print(f"Processed: {email_id}")
        except Exception as e:
            print(f"Exception occurred: {e}")

batch_process_worker()
        




            

            

