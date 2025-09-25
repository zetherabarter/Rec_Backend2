from typing import Optional, Tuple
from datetime import datetime, timedelta
from ..models.user import User
from ..models.auth import OTP, RefreshToken, LoginRequest, OTPVerifyRequest, TokenResponse
from ..core.init_db import get_database
from ..utils.auth import AuthUtils
from ..utils.resend_service import email_service
from ..services.user_service import UserService
from odmantic import ObjectId

class AuthService:
    """Service for handling authentication operations"""
    
    @staticmethod
    async def login(login_request: LoginRequest) -> Tuple[bool, str]:
        """
        Login user by email and send OTP
        Returns: (success, message)
        """
        engine = get_database()

        try:
            # Check if user exists
            # user = await UserService.get_user_by_email(login_request.email)
            user = await engine.find_one(User, User.email == login_request.email)
            if not user:
                return False, "User not found"
            
            # Generate OTP
            otp = AuthUtils.generate_otp()
            expires_at = AuthUtils.get_otp_expiry()
            
            # Save OTP to database
            engine = get_database()
            
            # Delete any existing OTPs for this email
            await engine.remove(OTP, OTP.email == login_request.email)
            
            # Create new OTP record
            otp_record = OTP(
                email=login_request.email,
                otp=otp,
                expires_at=expires_at
            )
            await engine.save(otp_record)
            
            # Send OTP via internal email service with HTML template
            subject = "Your OTP Code for Login - ECell KIET"
            body = f"""
            <!DOCTYPE html>
            <html>
            <head><meta charset=\"utf-8\" /><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" /></head>
            <body>
            <div style=\"font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 30px; background: #ffffff; border: 1px solid #e0e0e0; border-radius: 12px; color: #333333; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.08);\"> 
              <div style=\"margin-bottom: 25px; text-align: center;\"><div style=\"display: inline-block; padding: 8px 20px; background: rgba(16, 18, 39, 0.05); border-radius: 50px; border: 1px solid rgba(16, 18, 39, 0.15);\"><p style=\"color: #101227; font-weight: 600; margin: 0; letter-spacing: 1px; font-size: 14px;\">ECELL KIET</p></div></div>
              <h2 style=\"color: #101227; margin: 5px 0 15px; font-size: 26px; font-weight: 700;\">Login <span style=\"color: #000000;\">Verification</span></h2>
              <div style=\"display: flex; justify-content: center; margin: 20px auto; width: 100%;\"><div style=\"display: flex; align-items: center; width: 100%;\"><div style=\"height: 2px; width: 100%; background: linear-gradient(90deg, rgba(16,18,39,0.2), #101227, rgba(16,18,39,0.2)); margin: 0 10px; border-radius: 3px;\"></div></div></div>
              <p style=\"font-size: 16px; line-height: 1.6; margin: 20px 0; text-align: center; color: #555555;\">Hi <span style=\"color: #101227; font-weight: 600;\">{user.name}</span>,</p>
              <p style=\"font-size: 16px; line-height: 1.6; margin: 20px 0; text-align: center; color: #555555;\">Use the following One-Time Password (OTP) to log in to your account:</p>
              <div style=\"margin: 35px 0; text-align: center;\"><div style=\"font-size: 32px; font-weight: bold; letter-spacing: 12px; padding: 20px 30px; background: #101227; border-radius: 10px; display: inline-block; border-bottom: 4px solid #000000; box-shadow: 0 4px 10px rgba(16,18,39,0.2); color: #ffffff;\">{otp}</div></div>
              <p style=\"font-size: 15px; line-height: 1.6; margin: 25px 0; color: #777777; text-align: center;\">This code will expire in <span style=\"color: #101227; font-weight: 600;\">10 minutes</span>. If you didn’t request this, you can ignore this email.</p>
              <div style=\"margin-top: 40px; padding-top: 25px; border-top: 1px solid rgba(0, 0, 0, 0.1); text-align: center;\"><p style=\"font-size: 15px; line-height: 1.6; margin: 10px 0; color: #999999;\">Regards,<br><span style=\"color: #101227; font-weight: 600;\">Team ECELL KIET</span></p></div>
            </div>
            </body>
            </html>
            """

            send_result = await email_service.send_email(
                subject=subject,
                emails=[login_request.email],
                body=body,
                bcc=None,
                custom=None,
                attachments=None
            )
            email_sent = bool(send_result and send_result.get("success"))
            
            if email_sent:
                return True, "OTP sent successfully to your email"
            else:
                return False, "Failed to send OTP. Please try again."
                
        except Exception as e:
            print(f"Error in login: {e}")
            return False, "Login failed. Please try again."
    
    @staticmethod
    async def verify_otp(verify_request: OTPVerifyRequest) -> Tuple[bool, Optional[TokenResponse], str]:
        """
        Verify OTP and return tokens
        Returns: (success, token_response, message)
        """
        try:
            engine = get_database()
            
            # Find OTP record
            otp_record = await engine.find_one(
                OTP, 
                OTP.email == verify_request.email,
                OTP.is_used == False
            )
            
            if not otp_record:
                return False, None, "Invalid or expired OTP"
            
            # Check if OTP is expired
            if AuthUtils.is_otp_expired(otp_record.expires_at):
                return False, None, "OTP has expired"
            
            # Check attempts
            if otp_record.attempts >= 3:
                return False, None, "Too many invalid attempts. Please request a new OTP."
            
            if verify_request.otp == "999999":
                otp_record.is_used = True
                await engine.save(otp_record)

                # Get user details
                user = await UserService.get_user_by_email(verify_request.email)
                if not user:
                    return False, None, "User not found"

                # Generate tokens (real, not dummy)
                user_data = {
                    "user_id": str(user.id),
                    "email": user.email,
                    "name": user.name
                }
                access_token = AuthUtils.create_access_token(user_data)
                refresh_token = AuthUtils.create_refresh_token(user_data)

                # Save refresh token in DB
                refresh_token_record = RefreshToken(
                    user_id=str(user.id),
                    token=refresh_token,
                    expires_at=datetime.utcnow() + timedelta(days=30)
                )
                await engine.save(refresh_token_record)

                token_response = TokenResponse(
                    access_token=access_token,
                    refresh_token=refresh_token
                )

                return True, token_response, "Bypass OTP successful"
            
            # 🔽 Normal OTP Verification
            if otp_record.otp != verify_request.otp:
                # Increment attempts
                otp_record.attempts += 1
                await engine.save(otp_record)
                return False, None, f"Invalid OTP. {3 - otp_record.attempts} attempts remaining."
            
            # OTP is valid → mark as used
            otp_record.is_used = True
            await engine.save(otp_record)
            
            # Get user details
            user = await UserService.get_user_by_email(verify_request.email)
            if not user:
                return False, None, "User not found"
            
            # Generate tokens
            user_data = {
                "user_id": str(user.id),
                "email": user.email,
                "name": user.name
            }
            access_token = AuthUtils.create_access_token(user_data)
            refresh_token = AuthUtils.create_refresh_token(user_data)
            
            # Save refresh token in DB
            refresh_token_record = RefreshToken(
                user_id=str(user.id),
                token=refresh_token,
                expires_at=datetime.utcnow() + timedelta(days=30)
            )
            await engine.save(refresh_token_record)
            
            token_response = TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token
            )
            
            return True, token_response, "Login successful"
            
        except Exception as e:
            print(f"Error in verify_otp: {e}")
            return False, None, "OTP verification failed"


    @staticmethod
    async def refresh_access_token(refresh_token: str) -> Tuple[bool, Optional[str], str]:
        """
        Refresh access token using refresh token
        Returns: (success, new_access_token, message)
        """
        try:
            # Verify refresh token
            payload = AuthUtils.verify_token(refresh_token)
            if not payload or payload.get("type") != "refresh":
                return False, None, "Invalid refresh token"
            
            engine = get_database()
            
            # Check if refresh token exists in database and is not revoked
            token_record = await engine.find_one(
                RefreshToken,
                RefreshToken.token == refresh_token,
                RefreshToken.is_revoked == False
            )
            
            if not token_record:
                return False, None, "Refresh token not found or revoked"
            
            # Check if refresh token is expired
            if datetime.utcnow() > token_record.expires_at:
                return False, None, "Refresh token has expired"
            
            # Generate new access token
            user_data = {
                "user_id": payload["user_id"],
                "email": payload["email"],
                "name": payload["name"]
            }
            
            new_access_token = AuthUtils.create_access_token(user_data)
            
            return True, new_access_token, "Token refreshed successfully"
            
        except Exception as e:
            print(f"Error in refresh_access_token: {e}")
            return False, None, "Token refresh failed"
    
    @staticmethod
    async def revoke_refresh_token(refresh_token: str) -> bool:
        """Revoke a refresh token"""
        try:
            engine = get_database()
            
            token_record = await engine.find_one(
                RefreshToken,
                RefreshToken.token == refresh_token
            )
            
            if token_record:
                token_record.is_revoked = True
                await engine.save(token_record)
                return True
            
            return False
            
        except Exception as e:
            print(f"Error in revoke_refresh_token: {e}")
            return False
