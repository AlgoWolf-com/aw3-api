ARG FUNCTION_DIR=misc/update_name_servers

FROM public.ecr.aws/lambda/python:3.9 AS build-image

RUN pip3 install --upgrade pip wheel

ARG FUNCTION_DIR

COPY ${FUNCTION_DIR}/requirements.txt /build-image/

RUN pip3 install -r /build-image/requirements.txt \
       --disable-pip-version-check \
       --target "${LAMBDA_TASK_ROOT}"
       
FROM public.ecr.aws/lambda/python:3.9 as base-image

COPY --from=build-image ${LAMBDA_TASK_ROOT} ${LAMBDA_TASK_ROOT}

FROM base-image

ARG FUNCTION_DIR

# Copy function code
COPY ${FUNCTION_DIR}/ ${LAMBDA_TASK_ROOT}/

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "function.handler" ]
