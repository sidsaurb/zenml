---
description: Sending automated alerts to a Slack channel.
---

# Slack Alerter

The `SlackAlerter` enables you to send messages to a dedicated Slack channel directly from within your pipelines.

The `slack` integration also contains the following two standard steps:

* [slack\_alerter\_post\_step](https://apidocs.zenml.io/latest/integration\_code\_docs/integrations-slack/#zenml.integrations.slack.steps.slack\_alerter\_post\_step.slack\_alerter\_post\_step)
  takes a string, posts it to Slack, and returns `True` if the operation succeeded, else `False`.
* [slack\_alerter\_ask\_step](https://apidocs.zenml.io/latest/integration\_code\_docs/integrations-slack/#zenml.integrations.slack.steps.slack\_alerter\_ask\_step.slack\_alerter\_ask\_step)
  does the same as `slack_alerter_post_step`, but after sending the message, it waits until someone approves or rejects
  the operation from within Slack (e.g., by sending "approve" / "reject" to the bot in response)
  . `slack_alerter_ask_step` then only returns `True` if the operation succeeded and was approved, else `False`.

Interacting with Slack from within your pipelines can be very useful in practice:

* The `slack_alerter_post_step` allows you to get notified immediately when failures happen (e.g., model performance
  degradation, data drift, ...),
* The `slack_alerter_ask_step` allows you to integrate a human-in-the-loop into your pipelines before executing critical
  steps, such as deploying new models.

## How to use it

### Requirements

Before you can use the `SlackAlerter`, you first need to install ZenML's `slack` integration:

```shell
zenml integration install slack -y
```

{% hint style="info" %}
See the [Integrations](../integration-overview.md) page for more details on ZenML integrations and how to install and
use them.
{% endhint %}

### Setting Up a Slack Bot

In order to use the `SlackAlerter`, you first need to have a Slack workspace set up with a channel that you want your
pipelines to post to.

Then, you need to [create a Slack App](https://api.slack.com/apps?new\_app=1) with a bot in your workspace.

{% hint style="info" %}
Make sure to give your Slack bot `chat:write` and `chat:write.public` permissions in the `OAuth & Permissions` tab
under `Scopes`.
{% endhint %}

### Registering a Slack Alerter in ZenML

Next, you need to register a `slack` alerter in ZenML and link it to the bot you just created. You can do this with the
following command:

```shell
zenml alerter register slack_alerter \
    --flavor=slack \
    --slack_token=<SLACK_TOKEN> \
    --default_slack_channel_id=<SLACK_CHANNEL_ID>
```

Here is where you can find the required parameters:

* `<SLACK_CHANNEL_ID>`: Open your desired Slack channel in a browser, and copy out the last part of the URL starting
  with `C....`.
* `<SLACK_TOKEN>`: This is the Slack token of your bot. You can find it in the Slack app settings
  under `OAuth & Permissions`. **IMPORTANT**: Please make sure that the token is the `Bot User OAuth Token` not
  the `User OAuth Token`.

After you have registered the `slack_alerter`, you can add it to your stack like this:

```shell
zenml stack register ... -al slack_alerter
```

### How to Use the Slack Alerter

After you have a `SlackAlerter` configured in your stack, you can directly import
the [slack\_alerter\_post\_step](https://apidocs.zenml.io/latest/integration\_code\_docs/integrations-slack/#zenml.integrations.slack.steps.slack\_alerter\_post\_step.slack\_alerter\_post\_step)
and [slack\_alerter\_ask\_step](https://apidocs.zenml.io/latest/integration\_code\_docs/integrations-slack/#zenml.integrations.slack.steps.slack\_alerter\_ask\_step.slack\_alerter\_ask\_step)
steps and use them in your pipelines.

Since these steps expect a string message as input (which needs to be the output of another step), you typically also
need to define a dedicated formatter step that takes whatever data you want to communicate and generates the string
message that the alerter should post.

As an example, adding `slack_alerter_ask_step()` to your pipeline could look like this:

```python
from zenml.integrations.slack.steps.slack_alerter_ask_step import slack_alerter_ask_step
from zenml import step, pipeline


@step
def my_formatter_step(artifact_to_be_communicated) -> str:
    return f"Here is my artifact {artifact_to_be_communicated}!"


@pipeline
def my_pipeline(...):
    ...
    artifact_to_be_communicated = ...
    message = my_formatter_step(artifact_to_be_communicated)
    approved = slack_alerter_ask_step(message)
    ... # Potentially have different behavior in subsequent steps if `approved`

if __name__ == "__main__":
    my_pipeline()
```

For complete code examples of both Slack alerter steps, see
the [slack alerter example](https://github.com/zenml-io/zenml/tree/main/examples/slack\_alert), where we first send the
test accuracy of a model to Slack and then wait with model deployment until a user approves it in Slack.

For more information and a full list of configurable attributes of the Slack alerter, check out
the [API Docs](https://apidocs.zenml.io/latest/integration\_code\_docs/integrations-slack/#zenml.integrations.slack.alerters.slack\_alerter.SlackAlerter)
.
