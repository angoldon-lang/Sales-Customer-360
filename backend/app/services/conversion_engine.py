from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
from app.models.contract import Contract
from app.models.opportunity import Opportunity, OpportunityStatus
from app.models.conversion import ConversionRule, ConversionLog
from app.models.customer import Customer


class ConversionEngineService:
    """
    Motore di conversione automatica: licenze → opportunità di servizio.
    Analizza i contratti passati e suggerisce servizi basati su regole.
    """

    @staticmethod
    def run_conversion_engine(db: Session, customer_id: int | None = None) -> dict:
        """
        Esegui il motore di conversione per uno o tutti i clienti.

        Args:
            db: Sessione database
            customer_id: ID cliente (None = tutti)

        Returns:
            {
                "total_opportunities_created": int,
                "total_customers_processed": int,
                "errors": list[str]
            }
        """
        rules = db.query(ConversionRule).filter(ConversionRule.is_active == True).all()

        if not rules:
            return {
                "total_opportunities_created": 0,
                "total_customers_processed": 0,
                "errors": ["No active conversion rules found"]
            }

        customers = db.query(Customer).filter(Customer.status == "active")
        if customer_id:
            customers = customers.filter(Customer.id == customer_id)

        total_created = 0
        total_processed = 0
        errors = []

        for customer in customers:
            try:
                created = ConversionEngineService._process_customer(db, customer, rules)
                total_created += created
                total_processed += 1
            except Exception as e:
                errors.append(f"Customer {customer.id}: {str(e)}")

        db.commit()

        return {
            "total_opportunities_created": total_created,
            "total_customers_processed": total_processed,
            "errors": errors
        }

    @staticmethod
    def _process_customer(db: Session, customer: Customer, rules: list) -> int:
        """
        Processa un singolo cliente applicando tutte le regole attive.
        """
        created_count = 0

        for rule in rules:
            # Cerca contratti del cliente che matchano il trigger
            lookback_date = datetime.utcnow() - timedelta(days=rule.months_lookback * 30)

            trigger_contracts = db.query(Contract).filter(
                and_(
                    Contract.customer_id == customer.id,
                    Contract.product_id == rule.trigger_product_id,
                    Contract.start_date >= lookback_date,
                    Contract.status.in_(["active", "renewing"])
                )
            ).all()

            if not trigger_contracts:
                continue

            # Se la regola richiede che non esista un servizio attivo, verificalo
            if rule.requires_no_service:
                existing_service = db.query(Contract).filter(
                    and_(
                        Contract.customer_id == customer.id,
                        Contract.service_id == rule.recommended_service_id,
                        Contract.status == "active"
                    )
                ).first()

                if existing_service:
                    continue

            # Verifica se esiste già un'opportunità per questa combinazione
            existing_opportunity = db.query(Opportunity).filter(
                and_(
                    Opportunity.customer_id == customer.id,
                    Opportunity.service_id == rule.recommended_service_id,
                    Opportunity.status.in_([
                        OpportunityStatus.NEW,
                        OpportunityStatus.EVALUATING,
                        OpportunityStatus.ACCEPTED
                    ])
                )
            ).first()

            if existing_opportunity:
                continue

            # Crea l'opportunità
            for contract in trigger_contracts:
                trigger_contract = contract
                break

            opportunity = Opportunity(
                customer_id=customer.id,
                product_id=rule.trigger_product_id,
                service_id=rule.recommended_service_id,
                title=f"Propose {rule.name} for {customer.name}",
                description=f"Based on active {trigger_contract.product.name} contract",
                trigger=f"Product: {trigger_contract.product.name}",
                motivation=f"Customer has {trigger_contract.product.name} license without managed service",
                priority=rule.priority,
                status=OpportunityStatus.NEW,
                account_owner_id=None,
                estimated_value=None
            )

            db.add(opportunity)
            db.flush()

            # Log della conversione
            conversion_log = ConversionLog(
                rule_id=rule.id,
                customer_id=customer.id,
                opportunity_id=opportunity.id,
                trigger_contract_id=trigger_contract.id,
                trigger_product_name=trigger_contract.product.name,
                status="generated"
            )
            db.add(conversion_log)

            created_count += 1

        return created_count

    @staticmethod
    def get_conversion_stats(db: Session) -> dict:
        """Statistiche del motore di conversione."""
        total_rules = db.query(ConversionRule).filter(ConversionRule.is_active == True).count()
        active_rules = total_rules

        total_opportunities = db.query(Opportunity).count()
        new_opportunities = db.query(Opportunity).filter(
            Opportunity.status == OpportunityStatus.NEW
        ).count()
        accepted_opportunities = db.query(Opportunity).filter(
            Opportunity.status == OpportunityStatus.ACCEPTED
        ).count()

        total_logs = db.query(ConversionLog).count()

        acceptance_rate = 0
        if new_opportunities + accepted_opportunities > 0:
            acceptance_rate = round(
                (accepted_opportunities / (new_opportunities + accepted_opportunities)) * 100,
                2
            )

        return {
            "active_rules": active_rules,
            "total_opportunities": total_opportunities,
            "new_opportunities": new_opportunities,
            "accepted_opportunities": accepted_opportunities,
            "acceptance_rate": acceptance_rate,
            "total_conversions_logged": total_logs
        }

    @staticmethod
    def create_rule(
        db: Session,
        name: str,
        description: str,
        trigger_product_id: int,
        recommended_service_id: int,
        priority: str = "medium",
        months_lookback: int = 36,
        requires_no_service: bool = True
    ) -> dict:
        """Crea una nuova regola di conversione."""
        rule = ConversionRule(
            name=name,
            description=description,
            trigger_product_id=trigger_product_id,
            recommended_service_id=recommended_service_id,
            priority=priority,
            months_lookback=months_lookback,
            requires_no_service=requires_no_service,
            is_active=True
        )
        db.add(rule)
        db.commit()
        db.refresh(rule)

        return {
            "id": rule.id,
            "name": rule.name,
            "priority": rule.priority,
            "created_at": rule.created_at
        }
