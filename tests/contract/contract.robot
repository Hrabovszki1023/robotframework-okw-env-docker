*** Settings ***
Documentation    Contract smoke test: Docker provider must expose the OKW Env MVP keyword set.
Library          OkwEnvDocker

*** Variables ***
@{MVP_KEYWORDS}
...    Acquire Environment
...    Release Environment
...    Get Output
...    Render Template
...    List Outputs
...    Get Environment Id
...    Ensure Environment Ready
...    Reset Environment
...    Describe Environment
...    Validate Environment State

*** Test Cases ***
MVP Keywords Must Exist
    FOR    ${kw}    IN    @{MVP_KEYWORDS}
        Keyword Should Exist    ${kw}
    END
