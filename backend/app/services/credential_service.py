"""Credential management service implementing envelope encryption, rotation, and revocation."""

import datetime
import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError, ValidationError
from app.core.security import CredentialEncryptionService
from app.db.models.target import TargetCredential, Target
from app.domain.enums import CredentialKind, CredentialStatus
from app.services.base import BaseService


class CredentialService(BaseService):
    """Encapsulates target credentials envelope encryption and rotation lifecycle."""

    def add_target_credential(
        self,
        target_id: uuid.UUID,
        secret: str,
        kind: CredentialKind = CredentialKind.API_KEY,
    ) -> TargetCredential:
        """Encrypt secret plaintext and persist as TargetCredential."""
        if not secret:
            raise ValidationError("Credential secret cannot be empty")

        ciphertext, key_version, last4 = CredentialEncryptionService.encrypt_secret(secret)

        credential = TargetCredential(
            id=uuid.uuid4(),
            target_id=target_id,
            kind=kind,
            ciphertext=ciphertext,
            key_version=key_version,
            secret_last4=last4,
            status=CredentialStatus.ACTIVE,
        )
        self.db.add(credential)
        self.db.commit()
        self.db.refresh(credential)
        return credential

    def revoke_credential(self, target_id: uuid.UUID, credential_id: uuid.UUID) -> TargetCredential:
        """Revoke a target credential so it cannot be used by active jobs."""
        stmt = select(TargetCredential).where(
            TargetCredential.id == credential_id,
            TargetCredential.target_id == target_id,
        )
        cred = self.db.scalars(stmt).first()
        if not cred:
            raise NotFoundError(f"Credential {credential_id} not found for target {target_id}")

        cred.status = CredentialStatus.REVOKED
        cred.revoked_at = datetime.datetime.now(datetime.timezone.utc)
        self.db.commit()
        self.db.refresh(cred)
        return cred

    def get_active_credential_decrypted(self, target_id: uuid.UUID) -> Optional[str]:
        """
        Decrypt active credential in memory strictly for connector invocation.
        Never exposed over HTTP.
        """
        stmt = (
            select(TargetCredential)
            .where(
                TargetCredential.target_id == target_id,
                TargetCredential.status == CredentialStatus.ACTIVE,
            )
            .order_by(TargetCredential.created_at.desc())
        )
        cred = self.db.scalars(stmt).first()
        if not cred:
            return None

        return CredentialEncryptionService.decrypt_secret(cred.ciphertext, cred.key_version)

    def list_credentials_metadata(self, target_id: uuid.UUID) -> List[TargetCredential]:
        """List metadata of credentials associated with a target (never returning ciphertext)."""
        stmt = (
            select(TargetCredential)
            .where(TargetCredential.target_id == target_id)
            .order_by(TargetCredential.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())
