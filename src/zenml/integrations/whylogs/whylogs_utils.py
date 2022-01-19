#  Copyright (c) ZenML GmbH 2022. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at:
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
#  or implied. See the License for the specific language governing
#  permissions and limitations under the License.
import datetime
from typing import Dict, Optional

import pandas as pd
from whylogs import DatasetProfile  # type: ignore
from whylogs.app import Session  # type: ignore

from zenml.steps.step_context import StepContext


class WhylogsContext(StepContext):
    """Extends the base step context with whylogs session and logger management
    to facilitate whylogs data logging and profiling inside a step function.

    To use it, add a `WhylogsContext` object to the signature of your step
    function like this:

    @step
    def my_step(context: WhylogsContext, ...)
        ...
        context.log_dataframe(...)

    See `StepContext` for additional information on how step contexts can
    be used.

    **Note**: When using a `WhylogsContext` inside a step, ZenML disables
    caching for this step by default as the context provides access to external
    resources which might influence the result of your step execution. To
    enable caching anyway, explicitly enable it in the `@step` decorator or when
    initializing your custom step class.
    """

    _session: Session = None

    def get_whylogs_session(
        self,
    ) -> Session:
        """Returns the whylogs session associated with the current step.

        Args:
            output_name: Optional name of the output for which to get the
                materializer. If no name is given and the step only has a
                single output, the materializer of this output will be
                returned. If the step has multiple outputs, an exception
                will be raised.
            custom_materializer_class: If given, this `BaseMaterializer`
                subclass will be initialized with the output artifact instead
                of the materializer that was registered for this step output.

        Returns:
            A materializer initialized with the output artifact for
            the given output.
        """
        if self._session is not None:
            return self._session

        self._session = Session(
            project=self.step_name,
            # TODO: replace with pipeline name when available in the context
            pipeline=self.step_name,
            # keeping the writers list empty, serialization is done in the
            # materializer
            writers=[],
        )

        return self._session

    def log_dataframe(
        self,
        df: pd.DataFrame,
        dataset_name: Optional[str] = None,
        dataset_timestamp: Optional[datetime.datetime] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> DatasetProfile:
        """Log the statistics of a Pandas dataframe.

        Args:
            df: a Pandas dataframe to log.
            dataset_name: the name of the dataset (Optional). If not specified,
                the pipeline step name is used
            dataset_timestamp: timestamp to associate with the generated
                dataset profile (Optional). The current time is used if not
                supplied.
            tags: custom metadata tags associated with the whylogs profile

        Returns:
            A whylogs DatasetProfile with the statistics generated from the
            input dataset.
        """
        session = self.get_whylogs_session()
        # TODO: the step name is not sufficient to create a unique dataset
        # name across different pipelines. The pipeline name is also required
        dataset_name = dataset_name or self.step_name
        tags = tags or dict()
        # TODO: add more tags when this information is available in the context:
        # tags["zenml.pipeline"] = self.pipeline_name
        # tags["zenml.pipeline_run"] = self.pipeline_run_id
        tags["zenml.step"] = self.step_name
        # the datasetId tag is used to identify dataset profiles in whylabs.
        # dataset profiles with the same datasetID are considered to belong
        # to the same dataset/model.
        tags.setdefault("datasetId", dataset_name)
        logger = session.logger(
            dataset_name, dataset_timestamp=dataset_timestamp, tags=tags
        )
        logger.log_dataframe(df)
        return logger.close()
