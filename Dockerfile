###############################################################################
#
#       Fund Store Dev Image
#
###############################################################################

FROM ghcr.io/communitiesuk/fsd-base-dev/frontend:sha-68d9e31a4ff4adc9b5ead035e1a82203ec93d919 as self-serve-dev


WORKDIR /app

COPY . .

RUN python3 -m pip install --upgrade pip && pip install -r requirements.txt


