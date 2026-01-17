import passport from 'passport';
import { Strategy as GoogleStrategy } from 'passport-google-oauth20';
import prisma from './database';

passport.use(
  new GoogleStrategy(
    {
      clientID: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      callbackURL: process.env.GOOGLE_CALLBACK_URL!,
    },
    async (accessToken, refreshToken, profile, done) => {
      try {
        const email = profile.emails?.[0]?.value;
        
        if (!email) {
          return done(new Error('No email found in Google profile'), undefined);
        }

        // Check if user exists
        let user = await prisma.user.findUnique({
          where: { email },
        });

        if (!user) {
          // Create new user
          user = await prisma.user.create({
            data: {
              email,
              googleId: profile.id,
              name: profile.displayName,
              profilePicture: profile.photos?.[0]?.value,
            },
          });
        } else if (!user.googleId) {
          // Update existing user with Google ID
          user = await prisma.user.update({
            where: { id: user.id },
            data: {
              googleId: profile.id,
              profilePicture: user.profilePicture || profile.photos?.[0]?.value,
              name: user.name || profile.displayName,
            },
          });
        }

        return done(null, user);
      } catch (error) {
        return done(error as Error, undefined);
      }
    }
  )
);

export default passport;
