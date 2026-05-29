import cv2
import numpy as np
import os
import uuid

RESULT_FOLDER = 'results'
os.makedirs(RESULT_FOLDER, exist_ok=True)

def analyze_skin(image_path):
    """
    ENHANCED skin analysis with:
    - Better acne detection
    - Redness detection
    - Oily skin assessment
    - Dark spot detection
    - Dynamic recommendations based on actual findings
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            print(f"Cannot read image: {image_path}")
            return None

        original = image.copy()
        H, W = image.shape[:2]

        # ── Face Detection ──────────────────────────────
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        face_cascade = cv2.CascadeClassifier(cascade_path)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(60,60))

        if len(faces) > 0:
            faces = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)
            x, y, w, h = faces[0]
            pad = 15
            x1 = max(0, x - pad);  y1 = max(0, y - pad)
            x2 = min(W, x+w+pad);  y2 = min(H, y+h+pad)
            face_region = image[y1:y2, x1:x2]
            face_found = True
        else:
            x1,y1,x2,y2 = 0,0,W,H
            face_region = image
            face_found = False

        # ── CONVERT TO HSV ─────────────────────────────
        hsv = cv2.cvtColor(face_region, cv2.COLOR_BGR2HSV)
        
        # ── ACNE DETECTION (Red regions) ────────────────
        lower_red1 = np.array([0,   40, 40])
        upper_red1 = np.array([12, 255, 255])
        mask_acne1 = cv2.inRange(hsv, lower_red1, upper_red1)
        
        lower_red2 = np.array([158, 40, 40])
        upper_red2 = np.array([180, 255, 255])
        mask_acne2 = cv2.inRange(hsv, lower_red2, upper_red2)
        
        mask_acne = cv2.bitwise_or(mask_acne1, mask_acne2)
        
        # ── OILY SKIN DETECTION (High saturation) ──────
        lower_oily = np.array([0, 100, 80])    # High saturation = oily
        upper_oily = np.array([180, 255, 255])
        mask_oily = cv2.inRange(hsv, lower_oily, upper_oily)
        
        # ── DARK SPOTS (Low brightness) ────────────────
        lower_dark = np.array([0, 0, 0])
        upper_dark = np.array([180, 255, 80])   # Low V = dark
        mask_dark = cv2.inRange(hsv, lower_dark, upper_dark)
        
        # ── REDNESS DETECTION (High red, low blue) ─────
        b, g, r = cv2.split(face_region)
        redness = cv2.subtract(r, cv2.add(b, g) // 2)
        _, mask_redness = cv2.threshold(redness, 30, 255, cv2.THRESH_BINARY)
        
        # ── MORPHOLOGICAL OPERATIONS ────────────────────
        k = np.ones((3,3), np.uint8)
        mask_acne = cv2.morphologyEx(mask_acne, cv2.MORPH_OPEN, k, iterations=1)
        mask_acne = cv2.morphologyEx(mask_acne, cv2.MORPH_CLOSE, k, iterations=1)
        mask_acne = cv2.dilate(mask_acne, k, iterations=1)
        
        # ── COUNT ACNE SPOTS ────────────────────────────
        acne_contours, _ = cv2.findContours(mask_acne, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        valid_acne = [c for c in acne_contours if cv2.contourArea(c) > 25]
        acne_count = len(valid_acne)
        
        # ── ASSESS SKIN CONDITIONS ──────────────────────
        face_h, face_w = face_region.shape[:2]
        face_area = face_h * face_w
        
        # Oiliness percentage
        oily_pixels = cv2.countNonZero(mask_oily)
        oiliness_percent = (oily_pixels / face_area) * 100 if face_area > 0 else 0
        
        # Dark spots
        dark_contours, _ = cv2.findContours(mask_dark, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        dark_spots = [c for c in dark_contours if 40 < cv2.contourArea(c) < 800]
        dark_spot_count = len(dark_spots)
        
        # Redness level
        redness_pixels = cv2.countNonZero(mask_redness)
        redness_percent = (redness_pixels / face_area) * 100 if face_area > 0 else 0
        
        # ── DRAW RESULT IMAGE ──────────────────────────
        result = original.copy()
        
        if face_found:
            cv2.rectangle(result, (x1,y1), (x2,y2), (50,220,50), 2)
            cv2.putText(result, 'Face', (x1, y1-8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (50,220,50), 2)
        
        # Draw acne spots (RED circles)
        for cnt in valid_acne:
            (cx,cy), r = cv2.minEnclosingCircle(cnt)
            cx = int(cx)+x1;  cy = int(cy)+y1;  r = max(int(r),3)
            cv2.circle(result, (cx,cy), int(r)+4, (30,30,220), 2)
            cv2.circle(result, (cx,cy), 3, (30,30,220), -1)
        
        # Draw dark spots (BLUE circles - smaller)
        for cnt in dark_spots:
            (cx,cy), r = cv2.minEnclosingCircle(cnt)
            cx = int(cx)+x1;  cy = int(cy)+y1;  r = max(int(r),2)
            cv2.circle(result, (cx,cy), int(r)+2, (220,140,30), 1)
        
        # ── CALCULATE SCORE ────────────────────────────
        base_score = 100
        base_score -= acne_count * 4
        base_score -= dark_spot_count * 1
        base_score -= int(redness_percent / 2)
        base_score -= int(oiliness_percent / 5)
        skin_score = max(0, min(100, base_score))
        
        # ── DETERMINE SEVERITY ──────────────────────────
        if acne_count == 0 and redness_percent < 10:
            severity = 'Clear'
        elif acne_count <= 5 and redness_percent < 15:
            severity = 'Mild'
        elif acne_count <= 15 or redness_percent < 30:
            severity = 'Moderate'
        else:
            severity = 'Severe'
        
        # ── OVERLAY BANNER ──────────────────────────────
        banner = np.zeros((65, result.shape[1], 3), dtype=np.uint8)
        banner[:] = (18, 8, 28)
        
        score_color = (60,210,60) if skin_score>=70 else (60,190,220) if skin_score>=40 else (60,60,210)
        cv2.putText(banner, f'Score: {skin_score}/100', (10,24),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, score_color, 2)
        cv2.putText(banner, f'Acne: {acne_count}  Redness: {redness_percent:.0f}%  Oily: {oiliness_percent:.0f}%  Severity: {severity}', (10,50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180,180,180), 1)
        
        result = np.vstack([banner, result])
        
        # ── SAVE RESULT ─────────────────────────────────
        fname = 'result_' + uuid.uuid4().hex + '.jpg'
        fpath = os.path.join(RESULT_FOLDER, fname)
        cv2.imwrite(fpath, result)
        
        # ── DYNAMIC RECOMMENDATIONS ─────────────────────
        # These NOW CHANGE based on actual detected conditions
        recommendations = get_dynamic_recommendations(
            severity=severity,
            acne_count=acne_count,
            redness_percent=redness_percent,
            oiliness_percent=oiliness_percent,
            dark_spot_count=dark_spot_count,
            skin_score=skin_score
        )
        
        return {
            'result_path': fpath,
            'skin_score': skin_score,
            'acne_count': acne_count,
            'severity': severity,
            'recommendations': recommendations,
            # NEW: Pass detailed data for context-aware chatbot
            'acne_details': {
                'acne_count': acne_count,
                'redness_percent': float(redness_percent),
                'oiliness_percent': float(oiliness_percent),
                'dark_spot_count': dark_spot_count,
                'severity': severity
            }
        }
        
    except Exception as e:
        print(f"Analysis error: {e}")
        return None


def get_dynamic_recommendations(severity, acne_count, redness_percent, oiliness_percent, dark_spot_count, skin_score):
    """
    Generate recommendations DYNAMICALLY based on ACTUAL skin analysis results
    NOT static responses
    """
    recommendations = []
    
    # ── UNIVERSAL BASE (everyone gets these) ────────
    recommendations.append('Drink at least 8 glasses of water daily for hydration')
    recommendations.append('Get 7-8 hours of quality sleep each night')
    recommendations.append('Wash your face gently twice a day with mild cleanser')
    
    # ── ACNE-SPECIFIC ──────────────────────────────
    if acne_count > 0:
        if acne_count <= 3:
            recommendations.append('Spot-treat with 2% salicylic acid on active pimples')
            recommendations.append('Avoid picking or squeezing — let them heal naturally')
        elif acne_count <= 8:
            recommendations.append('Use salicylic acid cleanser (2%) morning and night')
            recommendations.append('Apply benzoyl peroxide 2.5% to affected areas')
            recommendations.append('Consider switching to non-comedogenic skincare products')
        else:
            recommendations.append('See a dermatologist for prescription acne treatment')
            recommendations.append('Use 10% benzoyl peroxide or higher')
            recommendations.append('Avoid dairy and high-glycemic foods which trigger acne')
            recommendations.append('Never pop pimples — causes scarring and spreads bacteria')
    
    # ── REDNESS-SPECIFIC ───────────────────────────
    if redness_percent > 15:
        if redness_percent <= 25:
            recommendations.append('Use a gentle, fragrance-free moisturizer to calm redness')
            recommendations.append('Wear SPF 30+ daily to prevent inflammation from UV exposure')
        else:
            recommendations.append('Apply calming ingredients: green tea or niacinamide')
            recommendations.append('Avoid hot water — use lukewarm when cleansing')
            recommendations.append('Stay away from spicy foods which can trigger flushing')
            recommendations.append('Consider a dermatologist visit for persistent redness')
    
    # ── OILY SKIN-SPECIFIC ─────────────────────────
    if oiliness_percent > 40:
        recommendations.append('Blot with oil-absorbing papers instead of touching your face')
        recommendations.append('Use a mattifying moisturizer (not cream)')
        if acne_count == 0:  # Oily but no acne
            recommendations.append('Lightweight sunscreen (gel or fluid, not cream)')
        recommendations.append('Limit foods high in omega-6 oils')
    
    # ── DARK SPOT-SPECIFIC ─────────────────────────
    if dark_spot_count > 3:
        recommendations.append('Use products with vitamin C to brighten dark spots')
        recommendations.append('Consistent SPF 30+ daily prevents spot darkening')
        recommendations.append('Consider professional treatments like laser for stubborn spots')
    
    # ── SEVERITY-BASED ESCALATION ──────────────────
    if severity == 'Severe':
        recommendations.insert(0, '⚠️ Schedule a dermatologist appointment soon')
        recommendations.append('Do not delay treatment — severe acne can cause scarring')
    elif severity == 'Moderate':
        recommendations.insert(0, '📋 Consider professional skincare treatment')
        if acne_count > 8:
            recommendations.append('Combination therapy (cleanser + treatment + moisturizer) works best')
    
    # ── GENERAL SKIN HEALTH ────────────────────────
    if skin_score >= 80:
        recommendations.insert(0, '✨ Your skin looks great! Keep up your routine')
    elif skin_score < 40:
        recommendations.append('Multiple issues detected — simplify routine, use one treatment at a time')
    
    return recommendations[:8]  # Return top 8 recommendations (max display)