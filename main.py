"""Importing requests module"""
import sys
import requests
import time 

UPLOAD_ENDPOINT = "https://api.assemblyai.com/v2/upload"
TRANSCRIPT_ENDPOINT  = "https://api.assemblyai.com/v2/transcript"
filename = sys.argv[1]
headers = {'authorization': "c73c61326667487c82528e3f2b15208c"}

"upload function to upload local audio file"
def upload(filename):
    def read_file(filename, chunk_size=5242880):
        with open(filename, 'rb') as _file:
            while True:
                data = _file.read(chunk_size)
                if not data:
                    break
                yield data

    upload_response = requests.post(UPLOAD_ENDPOINT,
                            headers=headers,
                            data=read_file(filename))
    audio_url = upload_response.json()['upload_url']
    return audio_url

"transcribe function"
def transcribe(audio_url):
    transcript_request = { "audio_url": audio_url }
    transcript_response = requests.post(TRANSCRIPT_ENDPOINT,json=transcript_request,headers=headers)
    job_id = transcript_response.json()['id']
    return job_id

"Polling function"
def poll(transcript_id):
    polling_endpoint = TRANSCRIPT_ENDPOINT + '/' + transcript_id
    polling_response = requests.get(polling_endpoint, headers=headers)
    return polling_response.json()


"get transcription result url function"
def get_transcription_result_url(audio_url):
    transcript_id = transcribe(audio_url)
    while True:
        data = poll(transcript_id)
        if data['status'] == 'completed':
            return data, None
        elif data['status'] == 'error':
            return data, data['error']

        print("Waiting 30 seconds...")
        time.sleep(30)


"Function to save transcript in a text file"
def save_transcript(audio_url):
    data, error = get_transcription_result_url(audio_url)
    if data:
        text_filename = filename + ".txt"
        with open(text_filename, "w") as f:
            f.write(data['text'])

        print("Transcription Saved!!")
    elif error:
        print("Error!!", error)

audio_url = upload(filename)
save_transcript(audio_url)
