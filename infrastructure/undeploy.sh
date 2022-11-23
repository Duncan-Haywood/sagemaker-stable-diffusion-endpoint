# you will also need to tear down resources that were bootstrapped and resources for the codepipeline. Google will give instructions.
echo "configure"
aws configure
echo "cdk destroy"
cdk destroy --force