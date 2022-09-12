# pylint: disable=redefined-outer-name,line-too-long
import time
from invoke import task, Collection

prod = Collection("prod")
dev = Collection("dev")
feature = Collection("feature")
namespace = Collection(prod, dev, feature)


@task
def build(ctx, template):
    ctx.run(f"sam build --template {template} --build-dir .aws-sam/build ")


@task
def deploy_global(ctx, profile=None):
    profile_str = ""
    if profile is not None:
        profile_str = f"--profile {profile} "

    build(ctx, "infrastructure/global-template.yaml")
    ctx.run(
        "sam deploy "
        f"{profile_str}"
        f"--stack-name aw3-global "
        f"--s3-bucket sam-$(aws sts get-caller-identity {profile_str} --no-cli-pager --query Account --output text) "
        f"--s3-prefix aw3-global "
        f"--region {ctx.AWS_REGION} "
        "--no-confirm-changeset "
        "--no-fail-on-empty-changeset "
        "--capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND "
        "--resolve-image-repos "
    )


@task
def deploy(ctx, profile=None, feature_name="", ttl="0"):
    stack_name = f"{ctx.ENV_NAME}"
    env_name = ctx.ENV_NAME

    profile_str = ""
    if profile is not None:
        profile_str = f"--profile {profile} "

    if ctx.COLLECTION_NAME == "feature":
        if not feature_name:
            raise AssertionError("dev environment must have feature_name")
        stack_name += f"-{feature_name}"
        env_name = f"{env_name}-{feature_name}".lower()
        repository_branch = feature_name
    else:
        if feature_name:
            raise AssertionError("Only dev environment can have feature_name")
        if ctx.COLLECTION_NAME == "prod":
            repository_branch = "production"
        elif ctx.COLLECTION_NAME == "dev":
            repository_branch = "main"

    ttl = str(int(time.time() + (int(ttl) * 86400)))

    build(ctx, "infrastructure/template.yaml")
    ctx.run(
        "sam deploy "
        f"{profile_str}"
        f"--stack-name {stack_name} "
        f"--s3-bucket sam-$(aws sts get-caller-identity {profile_str} --no-cli-pager --query Account --output text) "
        f"--s3-prefix {stack_name} "
        f"--region {ctx.AWS_REGION} "
        "--no-confirm-changeset "
        "--no-fail-on-empty-changeset "
        "--capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND "
        "--parameter-overrides "
        f'ParameterKey="EnvironmentName",ParameterValue="{env_name}" '
        f'ParameterKey="RepositoryBranch",ParameterValue="{repository_branch}" '
        f'ParameterKey="TTL",ParameterValue="{ttl}" '
        "--resolve-image-repos "
    )


for invoke_task in (build, deploy):
    prod.add_task(invoke_task)
    dev.add_task(invoke_task)
    feature.add_task(invoke_task)

prod.add_task(deploy_global)
dev.add_task(deploy_global)

prod.configure({"COLLECTION_NAME": "prod", "ENV_NAME": "aw3-prod"})
dev.configure({"COLLECTION_NAME": "dev", "ENV_NAME": "aw3-dev"})
feature.configure({"COLLECTION_NAME": "feature", "ENV_NAME": "aw3-dev"})
namespace.configure({"AWS_REGION": "ap-southeast-2"})
