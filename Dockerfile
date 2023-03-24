# syntax=docker/dockerfile:1

FROM python:3.11.2-alpine3.17
WORKDIR /hymns-api
COPY . .
ENV API_SECRET="<API_SECRET>"
ENV OTP_VERIFICATION_URL="https://<DOMAIN_NAME>/verify-otp"
ENV MAIL_USERNAME="<MAIL_USERNAME>"
ENV MAIL_PASSWORD="<MAIL_PASSWORD>"
ENV MAIL_FROM="<MAIL_FROM>"
ENV MAIL_PORT="<MAIL_PORT>"
ENV MAIL_SERVER="<MAIL_SERVER>"
ENV MAIL_DEBUG="0"
ENV MAIL_SUPPRESS_SEND="0"
RUN pip install --upgrade pip && pip install -r requirements.txt
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", ":8000", "main:app"]
EXPOSE 8000