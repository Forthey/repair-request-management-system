FROM ubuntu:22.04

COPY scripts/restore_volume_in_cont.sh .

ARG ARCHIVE_TO_BACKUP
ENV ARCHIVE_TO_BACKUP=$ARCHIVE_TO_BACKUP
CMD /restore_volume_in_cont.sh $ARCHIVE_TO_BACKUP