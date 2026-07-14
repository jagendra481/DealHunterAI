class RecommendationEngine:

    MINIMUM_SCANS = 5
    MINIMUM_UNIQUE_PRICES = 2
    MINIMUM_VARIATION_PERCENT = 1.0

    # ==========================================================
    # ANALYZE PRODUCT
    # ==========================================================

    @classmethod
    def analyze(
        cls,
        current_price,
        price_history
    ):

        current_price = float(
            current_price or 0
        )

        prices = [
            float(price)
            for price in price_history
            if (
                price is not None
                and float(price) > 0
            )
        ]

        scan_count = len(prices)

        # ======================================================
        # BASIC DATA VALIDATION
        # ==========================================================

        if current_price <= 0:

            return cls._collecting_result(
                scan_count,
                "A valid current price is required before "
                "DealHunterAI can analyse this product."
            )

        if scan_count < cls.MINIMUM_SCANS:

            return cls._collecting_result(
                scan_count,
                (
                    "DealHunterAI is collecting more price "
                    "history before giving a buy recommendation."
                )
            )

        lowest_price = min(prices)
        highest_price = max(prices)

        unique_prices = len(
            set(prices)
        )

        # ======================================================
        # PRICE VARIATION QUALITY
        # ==========================================================

        variation_percent = 0

        if lowest_price > 0:

            variation_percent = (
                (
                    highest_price
                    - lowest_price
                )
                / lowest_price
            ) * 100

        if unique_prices < cls.MINIMUM_UNIQUE_PRICES:

            return cls._collecting_result(
                scan_count,
                (
                    "The tracked price has remained unchanged. "
                    "DealHunterAI needs price variation before "
                    "giving a reliable buy recommendation."
                ),
                lowest_price,
                highest_price
            )

        if (
            variation_percent
            < cls.MINIMUM_VARIATION_PERCENT
        ):

            return cls._collecting_result(
                scan_count,
                (
                    "Only minor price variation has been "
                    "recorded. More meaningful price movement "
                    "is needed for a reliable recommendation."
                ),
                lowest_price,
                highest_price
            )

        # ======================================================
        # DISTANCE FROM HISTORICAL LOW
        # ==========================================================

        above_low_percent = (
            (
                current_price
                - lowest_price
            )
            / lowest_price
        ) * 100

        # ======================================================
        # RECENT PRICE TREND
        # ==========================================================

        recent_prices = prices[-5:]

        falling_count = 0
        rising_count = 0

        for index in range(
            1,
            len(recent_prices)
        ):

            previous_price = (
                recent_prices[index - 1]
            )

            price = recent_prices[index]

            if price < previous_price:

                falling_count += 1

            elif price > previous_price:

                rising_count += 1

        if falling_count > rising_count:

            trend = "FALLING"

        elif rising_count > falling_count:

            trend = "RISING"

        else:

            trend = "STABLE"

        # ======================================================
        # PRICE RANGE POSITION
        # ==========================================================

        price_range = (
            highest_price
            - lowest_price
        )

        price_position = (
            (
                current_price
                - lowest_price
            )
            / price_range
        ) * 100

        # ======================================================
        # BUY OPPORTUNITY SCORE
        # ==========================================================

        buy_score = 50

        # Distance from historical low

        if above_low_percent <= 2:

            buy_score += 25

        elif above_low_percent <= 5:

            buy_score += 18

        elif above_low_percent <= 10:

            buy_score += 8

        elif above_low_percent >= 20:

            buy_score -= 25

        # Position inside historical range

        if price_position <= 20:

            buy_score += 15

        elif price_position <= 40:

            buy_score += 5

        elif price_position >= 80:

            buy_score -= 15

        # Recent trend

        if trend == "FALLING":

            buy_score -= 10

        elif trend == "RISING":

            buy_score += 5

        # History confidence

        if scan_count >= 20:

            history_confidence = 100

        elif scan_count >= 15:

            history_confidence = 85

        elif scan_count >= 10:

            history_confidence = 70

        else:

            history_confidence = 50

        buy_score = max(
            0,
            min(100, buy_score)
        )

        confidence = round(
            (
                buy_score * 0.7
            )
            + (
                history_confidence * 0.3
            )
        )

        # ======================================================
        # FINAL RECOMMENDATION
        # ==========================================================

        if (
            buy_score >= 75
            and above_low_percent <= 5
        ):

            recommendation = "BUY_NOW"

            reason = (
                "The current price is close to the lowest "
                "price recorded by DealHunterAI and compares "
                "favourably with its tracked price range."
            )

        elif (
            trend == "FALLING"
            or buy_score >= 45
        ):

            recommendation = "WAIT"

            if trend == "FALLING":

                reason = (
                    "The recent tracked price trend is falling. "
                    "Waiting may provide a better buying "
                    "opportunity."
                )

            else:

                reason = (
                    "The current price is not yet a strong "
                    "historical buying opportunity. Consider "
                    "waiting for a better tracked price."
                )

        else:

            recommendation = "EXPENSIVE"

            reason = (
                "The current price is high compared with the "
                "price range recorded by DealHunterAI."
            )

        estimated_saving = max(
            current_price - lowest_price,
            0
        )

        return {
            "recommendation": recommendation,
            "confidence": confidence,
            "reason": reason,
            "estimated_saving": round(
                estimated_saving,
                2
            ),
            "trend": trend,
            "lowest_price": lowest_price,
            "highest_price": highest_price,
            "above_low_percent": round(
                above_low_percent,
                1
            ),
            "variation_percent": round(
                variation_percent,
                1
            ),
            "unique_prices": unique_prices,
            "scan_count": scan_count
        }

    # ==========================================================
    # COLLECTING DATA RESULT
    # ==========================================================

    @staticmethod
    def _collecting_result(
        scan_count,
        reason,
        lowest_price=0,
        highest_price=0
    ):

        return {
            "recommendation": "COLLECTING",
            "confidence": 0,
            "reason": reason,
            "estimated_saving": 0,
            "trend": "STABLE",
            "lowest_price": lowest_price,
            "highest_price": highest_price,
            "above_low_percent": 0,
            "variation_percent": 0,
            "unique_prices": 1 if scan_count else 0,
            "scan_count": scan_count
        }
