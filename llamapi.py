import json
import sys

import requests

url = "http://localhost:8080/completion"
headers = {"Content-Type": "application/json"}


def get_response(
    prompt,
    temperature=0.8,
    top_k=40,
    top_p=0.9,
    n_predict=128,
    n_keep=0,
    stop=[],
    tfs_z=1.0,
    typical_p=1.0,
    repeat_penalty=1.1,
    repeat_last_n=64,
    penalize_nl=True,
    presence_penalty=0.0,
    frequency_penalty=0.0,
    mirostat=0,
    mirostat_tau=5.0,
    mirostat_eta=0.1,
    seed=-1,
    ignore_eos=False,
    logit_bias=[],
):
    """
    temperature: Adjust the randomness of the generated text (default: 0.8).
    top_k: Limit the next token selection to the K most probable tokens (default: 40).
    top_p: Limit the next token selection to a subset of tokens with a cumulative probability above a threshold P (default: 0.9).
    n_predict: Set the number of tokens to predict when generating text. Note: May exceed the set limit slightly if the last token is a partial multibyte character. When 0, no tokens will be generated but the prompt is evaluated into the cache. (default: 128, -1 = infinity).
    n_keep: Specify the number of tokens from the initial prompt to retain when the model resets its internal context. By default, this value is set to 0 (meaning no tokens are kept). Use -1 to retain all tokens from the initial prompt.
    stream: It allows receiving each predicted token in real-time instead of waiting for the completion to finish. To enable this, set to true.
    prompt: Provide a prompt. Internally, the prompt is compared, and it detects if a part has already been evaluated, and the remaining part will be evaluate. A space is inserted in the front like main.cpp does.
    stop: Specify a JSON array of stopping strings. These words will not be included in the completion, so make sure to add them to the prompt for the next iteration (default: []).
    tfs_z: Enable tail free sampling with parameter z (default: 1.0, 1.0 = disabled).
    typical_p: Enable locally typical sampling with parameter p (default: 1.0, 1.0 = disabled).
    repeat_penalty: Control the repetition of token sequences in the generated text (default: 1.1).
    repeat_last_n: Last n tokens to consider for penalizing repetition (default: 64, 0 = disabled, -1 = ctx-size).
    penalize_nl: Penalize newline tokens when applying the repeat penalty (default: true).
    presence_penalty: Repeat alpha presence penalty (default: 0.0, 0.0 = disabled).
    frequency_penalty: Repeat alpha frequency penalty (default: 0.0, 0.0 = disabled);
    mirostat: Enable Mirostat sampling, controlling perplexity during text generation (default: 0, 0 = disabled, 1 = Mirostat, 2 = Mirostat 2.0).
    mirostat_tau: Set the Mirostat target entropy, parameter tau (default: 5.0).
    mirostat_eta: Set the Mirostat learning rate, parameter eta (default: 0.1).
    seed: Set the random number generator (RNG) seed (default: -1, -1 = random seed).
    ignore_eos: Ignore end of stream token and continue generating (default: false).
    logit_bias: Modify the likelihood of a token appearing in the generated text completion. For example, use "logit_bias": [[15043,1.0]] to increase the likelihood of the token 'Hello', or "logit_bias": [[15043,-1.0]] to decrease its likelihood. Setting the value to false, "logit_bias": [[15043,false]] ensures that the token Hello is never produced (default: []).
    """
    data = {
        "prompt": prompt,
        "temperature": temperature,
        "top_k": top_k,
        "top_p": top_p,
        "n_predict": n_predict,
        "n_keep": n_keep,
        "stream": False,
        "stop": stop,
        "tfs_z": tfs_z,
        "typical_p": typical_p,
        "repeat_penalty": repeat_penalty,
        "repeat_last_n": repeat_last_n,
        "penalize_nl": penalize_nl,
        "presence_penalty": presence_penalty,
        "frequency_penalty": frequency_penalty,
        "mirostat": mirostat,
        "mirostat_tau": mirostat_tau,
        "mirostat_eta": mirostat_eta,
        "seed": seed,
        "ignore_eos": ignore_eos,
        "logit_bias": logit_bias,
    }
    res = requests.post(url, headers=headers, data=json.dumps(data))
    return json.loads(res.text)["content"]  # type: ignore

def stream_response(
    prompt,
    temperature=0.8,
    top_k=40,
    top_p=0.9,
    n_predict=128,
    n_keep=0,
    stop=[],
    tfs_z=1.0,
    typical_p=1.0,
    repeat_penalty=1.1,
    repeat_last_n=64,
    penalize_nl=True,
    presence_penalty=0.0,
    frequency_penalty=0.0,
    mirostat=0,
    mirostat_tau=5.0,
    mirostat_eta=0.1,
    seed=-1,
    ignore_eos=False,
    logit_bias=[],
        ):

    data = {
        "prompt": prompt,
        "temperature": temperature,
        "top_k": top_k,
        "top_p": top_p,
        "n_predict": n_predict,
        "n_keep": n_keep,
        "stream": True,
        "stop": stop,
        "tfs_z": tfs_z,
        "typical_p": typical_p,
        "repeat_penalty": repeat_penalty,
        "repeat_last_n": repeat_last_n,
        "penalize_nl": penalize_nl,
        "presence_penalty": presence_penalty,
        "frequency_penalty": frequency_penalty,
        "mirostat": mirostat,
        "mirostat_tau": mirostat_tau,
        "mirostat_eta": mirostat_eta,
        "seed": seed,
        "ignore_eos": ignore_eos,
        "logit_bias": logit_bias,
    }

    # Streaming response
    with requests.post(url, headers=headers, data=json.dumps(data), stream=True) as res:
        for token in res.iter_lines():
            if token: 
                data = token.decode("utf-8")
                text = (
                    json.loads("{" + data.replace("data", '"data"') + "}")["data"][
                        "content"
                    ]
                )
                yield text


def stream(message, n_predict=128):
    data = {
        "prompt": message,
        "n_predict": n_predict,
        "stream": True,
    }
    with requests.post(url, headers=headers, data=json.dumps(data), stream=True) as res:
        for token in res.iter_lines():
            if token:
                data = token.decode("utf-8")
                sys.stdout.write(
                    json.loads("{" + data.replace("data", '"data"') + "}")["data"][
                        "content"
                    ]
                )
                sys.stdout.flush()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--stream", action="store_true")
    parser.add_argument("-m", "--message", type=str, default="Hello World!")
    args = parser.parse_args()

    if args.stream:
        stream(args.message)
    else:
        req(args.message)
