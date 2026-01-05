# Generated from RSimple.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .RSimpleParser import RSimpleParser
else:
    from RSimpleParser import RSimpleParser

# This class defines a complete generic visitor for a parse tree produced by RSimpleParser.

class RSimpleVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by RSimpleParser#program.
    def visitProgram(self, ctx:RSimpleParser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSimpleParser#statementList.
    def visitStatementList(self, ctx:RSimpleParser.StatementListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSimpleParser#statement.
    def visitStatement(self, ctx:RSimpleParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSimpleParser#assignment.
    def visitAssignment(self, ctx:RSimpleParser.AssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSimpleParser#assignOp.
    def visitAssignOp(self, ctx:RSimpleParser.AssignOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSimpleParser#outputStatement.
    def visitOutputStatement(self, ctx:RSimpleParser.OutputStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSimpleParser#expressionList.
    def visitExpressionList(self, ctx:RSimpleParser.ExpressionListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSimpleParser#ifStatement.
    def visitIfStatement(self, ctx:RSimpleParser.IfStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSimpleParser#whileStatement.
    def visitWhileStatement(self, ctx:RSimpleParser.WhileStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSimpleParser#statementBlock.
    def visitStatementBlock(self, ctx:RSimpleParser.StatementBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSimpleParser#expression.
    def visitExpression(self, ctx:RSimpleParser.ExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSimpleParser#arithmExpression.
    def visitArithmExpression(self, ctx:RSimpleParser.ArithmExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSimpleParser#term.
    def visitTerm(self, ctx:RSimpleParser.TermContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSimpleParser#power.
    def visitPower(self, ctx:RSimpleParser.PowerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSimpleParser#factor.
    def visitFactor(self, ctx:RSimpleParser.FactorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSimpleParser#primary.
    def visitPrimary(self, ctx:RSimpleParser.PrimaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSimpleParser#relOp.
    def visitRelOp(self, ctx:RSimpleParser.RelOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by RSimpleParser#boolConst.
    def visitBoolConst(self, ctx:RSimpleParser.BoolConstContext):
        return self.visitChildren(ctx)



del RSimpleParser